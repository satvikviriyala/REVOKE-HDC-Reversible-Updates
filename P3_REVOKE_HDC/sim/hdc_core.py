"""
Core HDC Operations, Prototype Memory, and Multi-Modal Feature Encoder.
"""

import math
import random
import zlib
from typing import Dict, List, Tuple


def sign_threshold(x: int) -> int:
    """
    Frozen sign threshold convention:
    sign_threshold(x) = 1 if x >= 0 else 0.
    """
    return 1 if x >= 0 else 0


class PrototypeMemory:
    """
    Bit-true simulation of 4-class, 64-bit word-packed prototype memory.
    D = 4096 bits per class (64 words of 64 bits = 512 bytes per class).
    Total storage: 2048 bytes across 4 classes.
    """

    def __init__(self, seed: int = 0x20261001):
        self.num_classes = 4
        self.words_per_class = 64
        self.dimension = 4096
        # words[class_id][word_idx] -> uint64
        self.words: List[List[int]] = [[0] * self.words_per_class for _ in range(self.num_classes)]
        self._init_prototypes(seed)

    def _init_prototypes(self, seed: int):
        rng = random.Random(seed)
        for c in range(self.num_classes):
            for w in range(self.words_per_class):
                # 64 random bits per word
                self.words[c][w] = rng.getrandbits(64)

    def get_bit(self, class_id: int, dim: int) -> int:
        assert 0 <= class_id < self.num_classes
        assert 0 <= dim < self.dimension
        word_idx = dim >> 6
        bit_idx = dim & 63
        return (self.words[class_id][word_idx] >> bit_idx) & 1

    def set_bit(self, class_id: int, dim: int, bit: int):
        assert 0 <= class_id < self.num_classes
        assert 0 <= dim < self.dimension
        assert bit in (0, 1)
        word_idx = dim >> 6
        bit_idx = dim & 63
        if bit == 1:
            self.words[class_id][word_idx] |= (1 << bit_idx)
        else:
            self.words[class_id][word_idx] &= ~(1 << bit_idx)

    def apply_masked_update(self, class_id: int, dim_bit_pairs: List[Tuple[int, int]]) -> int:
        """
        Groups entries by 64-bit word and performs one masked read-modify-write per word.
        Returns the number of unique 64-bit words modified.
        """
        assert 0 <= class_id < self.num_classes
        word_groups: Dict[int, List[Tuple[int, int]]] = {}
        for dim, bit in dim_bit_pairs:
            assert 0 <= dim < self.dimension
            assert bit in (0, 1)
            w_idx = dim >> 6
            b_idx = dim & 63
            if w_idx not in word_groups:
                word_groups[w_idx] = []
            word_groups[w_idx].append((b_idx, bit))

        for w_idx, pairs in word_groups.items():
            mask = 0
            val = 0
            for b_idx, bit in pairs:
                bit_mask = 1 << b_idx
                mask |= bit_mask
                if bit == 1:
                    val |= bit_mask
            old_word = self.words[class_id][w_idx]
            new_word = (old_word & ~mask) | (val & mask)
            self.words[class_id][w_idx] = new_word

        return len(word_groups)

    def get_prototype_bytes(self, class_id: int) -> bytes:
        """Returns 512 bytes representing the packed prototype."""
        assert 0 <= class_id < self.num_classes
        out = bytearray(512)
        for w_idx in range(self.words_per_class):
            w_val = self.words[class_id][w_idx]
            out[w_idx * 8 : (w_idx + 1) * 8] = w_val.to_bytes(8, byteorder="little")
        return bytes(out)

    def get_crc32(self, class_id: int) -> int:
        """Computes CRC-32 over the 512-byte packed prototype."""
        return zlib.crc32(self.get_prototype_bytes(class_id)) & 0xFFFFFFFF

    def clone_state(self) -> List[List[int]]:
        """Returns an exact copy of the prototype memory."""
        return [list(row) for row in self.words]

    def restore_state(self, saved_state: List[List[int]]):
        """Restores exact prototype memory from saved state."""
        self.words = [list(row) for row in saved_state]

    def hamming_distance(self, class_id: int, query_bits: List[int]) -> int:
        """Computes Hamming distance between query bits and stored prototype."""
        assert len(query_bits) == self.dimension
        dist = 0
        for dim in range(self.dimension):
            stored_b = self.get_bit(class_id, dim)
            if stored_b != query_bits[dim]:
                dist += 1
        return dist


class MultiModalEncoder:
    """
    Multi-modal HDC Feature Encoder simulating:
    - Modality A: Vision-style stream (32 continuous features)
    - Modality B: IMU-style stream (16 continuous features)
    Generates 4096-D hypervectors using continuous random projection item memory.
    """

    def __init__(self, seed: int = 0x20261001, dimension: int = 4096):
        self.dimension = dimension
        self.rng = random.Random(seed)
        # Random projection matrices for modalities A and B
        self.num_features_A = 32
        self.num_features_B = 16
        # Generate bipolar projection vectors {-1, +1}
        self.basis_A = [
            [1 if self.rng.random() >= 0.5 else -1 for _ in range(dimension)]
            for _ in range(self.num_features_A)
        ]
        self.basis_B = [
            [1 if self.rng.random() >= 0.5 else -1 for _ in range(dimension)]
            for _ in range(self.num_features_B)
        ]

    def encode_modality_A(self, features: List[float]) -> List[int]:
        """Encodes 32 features to 4096-D binary hypervector."""
        accum = [0.0] * self.dimension
        for i, val in enumerate(features[: self.num_features_A]):
            for d in range(self.dimension):
                accum[d] += val * self.basis_A[i][d]
        return [1 if accum[d] >= 0 else 0 for d in range(self.dimension)]

    def encode_modality_B(self, features: List[float]) -> List[int]:
        """Encodes 16 features to 4096-D binary hypervector."""
        accum = [0.0] * self.dimension
        for i, val in enumerate(features[: self.num_features_B]):
            for d in range(self.dimension):
                accum[d] += val * self.basis_B[i][d]
        return [1 if accum[d] >= 0 else 0 for d in range(self.dimension)]

    def evaluate_sample(
        self, proto_mem: PrototypeMemory, true_class: int, noise_level: float = 0.05
    ) -> Tuple[int, int, int, int]:
        """
        Simulates two modalities evaluating a sample:
        Returns (hA, mA, hB, mB).
        Margins are normalized to 0..255.
        """
        # Distances from true class
        base_distances = [
            proto_mem.hamming_distance(c, [proto_mem.get_bit(true_class, d) for d in range(4096)])
            for c in range(4)
        ]

        # Add small independent sensor noise
        dist_A = [d + self.rng.randint(0, int(noise_level * 500)) for d in base_distances]
        dist_B = [d + self.rng.randint(0, int(noise_level * 500)) for d in base_distances]

        # Best and second best for A
        sorted_A = sorted(range(4), key=lambda c: dist_A[c])
        hA = sorted_A[0]
        margin_A_raw = dist_A[sorted_A[1]] - dist_A[sorted_A[0]]
        mA = min(255, max(0, int(margin_A_raw * 2.5)))

        # Best and second best for B
        sorted_B = sorted(range(4), key=lambda c: dist_B[c])
        hB = sorted_B[0]
        margin_B_raw = dist_B[sorted_B[1]] - dist_B[sorted_B[0]]
        mB = min(255, max(0, int(margin_B_raw * 2.5)))

        return hA, mA, hB, mB
