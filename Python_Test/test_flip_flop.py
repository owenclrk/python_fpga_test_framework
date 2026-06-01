import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ReadOnly

#Function to reset DUT by waiting for clock 
async def reset_dut(dut,duration_ns=10):
    """Assert reset for duration_ns, then release and wait for the DUT to settle."""
    #Set Reset to 1 and D input to 0
    dut.rst.value = 1
    dut.d.value = 0
    #Wait for values to settle
    await Timer(duration_ns, unit="ns")
    #Wait for next rising clock edge
    await RisingEdge(dut.clk)
    #Set Reset to O
    dut.rst.value = 0
    #Wait one clock cycle for post-reset
    await RisingEdge(dut.clk) 
    #Check the values are asserted correctly 
    assert dut.rst.value == 0, f"Reset release failed: rst={dut.rst.value}, expected 0"
    assert dut.q.value == 0,   f"DUT not in reset state: q={dut.q.value}, expected 0"
    dut._log.info("Reset complete")


@cocotb.test()
async def test_reset(dut):
    """Test that reset drives Q low."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
 
    #Set D Value
    dut.d.value = 1
    #Wait for a half clock cycle to trigger the reset
    await Timer(5, unit="ns")
    #Set Reset value
    dut.rst.value = 1
    await Timer(5, unit="ns")
    #Assert output value is set to 0
    assert dut.q.value == 0, f"Reset failed: q={dut.q.value}, expected 0"
    dut._log.info("PASS: Reset drives Q=0 regardless of D")

@cocotb.test()
async def test_d_captures_high(dut):
    '''Test D=1 is captured on rising clock edge'''
    cocotb.start_soon(Clock(dut.clk,10,unit="ns").start())
    await reset_dut(dut)
    #Set the D pin high
    dut.d.value = 1
    #Wait for rising clock edge
    await RisingEdge(dut.clk)
    #Allow data to settle before checking assert
    await Timer(1,unit="ns")
    assert dut.q.value == 1, f'Captured high failed: q={dut.q.value},expected 1'
    dut._log.info("Pass: Q captured D=1")

@cocotb.test()
async def test_d_release_low(dut):
    '''Test D=0 is captured on rising clock edge and latched by Q'''
    cocotb.start_soon(Clock(dut.clk,10,unit="ns").start())
    await reset_dut(dut)

    dut.d.value = 1
    await RisingEdge(dut.clk)
    await Timer(1,unit="ns")

    dut.d.value = 0
    await RisingEdge(dut.clk)
    await Timer(1,unit="ns")

    assert dut.q.value == 0, f'Captured high failed: q={dut.q.value},expected 0'
    dut._log.info("Pass: Q captured D=1")

@cocotb.test()
async def test_d_mid_cycle(dut):
    '''Test D=1 is captured on rising clock edge'''
    cocotb.start_soon(Clock(dut.clk,10,unit="ns").start())
    await reset_dut(dut)

    dut.d.value = 1
    await RisingEdge(dut.clk)
    await Timer(1,unit="ns") 

    captured_q = int(dut.q.value)
    dut.d.value = 0
    await Timer(4,unit="ns")

    assert dut.q.value == captured_q, f"Q changed mid-cycle: q{dut.q.value}, expected {captured_q}"
    dut._log.info("PASS: Q holds value between clock edges")


@cocotb.test()
async def test_toggle_sequence(dut):
    cocotb.start_soon(Clock(dut.clk,10,unit="ns").start())
    await reset_dut(dut)

    #Provide a sequence of data and check the q value matches the corresponding output
    pattern = [1,0,1,1,0,0,1,0]
    for i, val in enumerate(pattern):
        dut.d.value = val
        await RisingEdge(dut.clk)
        await Timer(1,unit="ns")
        assert dut.q.value == val, f"Cycle {i}: q={dut.q.value},expected{val}"
    
    dut._log.info(f"Pass: Toggle Sequence {pattern} captured correctly")