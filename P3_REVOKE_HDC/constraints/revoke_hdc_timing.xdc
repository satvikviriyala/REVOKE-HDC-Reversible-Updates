# REVOKE-HDC Timing Constraints for Xilinx Kria KV260 (xczu5ev-sfvc784-1-i)
# Clock definition for primary PL processing clock

create_clock -period 10.000 -name clk_pl_100mhz [get_ports clk]

# Set input and output delays with respect to 100 MHz clock (nominal 2.0ns budget)
set_input_delay -clock clk_pl_100mhz -max 2.500 [get_ports {pkt_data* pkt_valid restore_req s_axi_*}]
set_input_delay -clock clk_pl_100mhz -min 0.500 [get_ports {pkt_data* pkt_valid restore_req s_axi_*}]

set_output_delay -clock clk_pl_100mhz -max 2.500 [get_ports {outcome_code* wr_en_out s_axi_*}]
set_output_delay -clock clk_pl_100mhz -min 0.500 [get_ports {outcome_code* wr_en_out s_axi_*}]
