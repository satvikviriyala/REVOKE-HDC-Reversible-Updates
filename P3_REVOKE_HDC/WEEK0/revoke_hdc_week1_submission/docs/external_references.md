# External technical references used for the R1 implementation choices

These references are not substitutes for the project README/PROJECT_PLAN; they only support platform-level facts used in the R1 engineering decisions.

1. AMD Kria KV260 Vision AI Starter Kit Data Sheet DS986, Product Details / Summary. The board uses a Zynq UltraScale+ MPSoC and lists 144 Block RAM blocks. https://docs.amd.com/r/en-US/ds986-kv260-starter-kit/Product-Details
2. AMD Kria KV260 Vision AI Starter Kit User Guide UG1089, Summary. https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Summary
3. AMD Zynq UltraScale+ MPSoC Processing System Product Guide PG201, PS-PL AXI interfaces. `M_AXI_HPM0_FPD` and `M_AXI_HPM1_FPD` are PS master interfaces to PL slaves. https://docs.amd.com/r/en-US/pg201-zynq-ultrascale-plus-processing-system/Slave-Interface
