# D Flip-Flop — Verification with cocotb

A simple synchronous D flip-flop written in SystemVerilog, verified using [cocotb](https://www.cocotb.org/) and simulated with [Icarus Verilog](https://steveicarus.github.io/iverilog/).

---

## Design — `flip_flop.sv`

The design under test (DUT) is a positive-edge-triggered D flip-flop with asynchronous active-high reset.

| Port  | Direction | Width | Description                      |
| ----- | --------- | ----- | -------------------------------- |
| `d`   | input     | 1-bit | Data input                       |
| `clk` | input     | 1-bit | Clock (rising-edge triggered)    |
| `rst` | input     | 1-bit | Asynchronous reset (active-high) |
| `q`   | output    | 1-bit | Registered data output           |

**Behaviour:**

- On a rising edge of `rst`: `q` is forced to `0` immediately (asynchronous).
- On a rising edge of `clk` (while `rst` is low): `q` captures the current value of `d`.

---

## Project Structure

```
.
├── flip_flop.sv              # DUT — SystemVerilog source
├── test_flip_flop.py         # cocotb testbench
├── Makefile                  # Build & simulation rules
```

---

## Prerequisites

| Tool                                                                           | Purpose                          |
| ------------------------------------------------------------------------------ | -------------------------------- |
| [Icarus Verilog](https://steveicarus.github.io/iverilog/) (`iverilog` / `vvp`) | HDL simulation                   |
| [cocotb](https://docs.cocotb.org/en/stable/install.html) ≥ 1.7                 | Python-based testbench framework |
| Python ≥ 3.8                                                                   | Test execution                   |

Install cocotb:

```bash
pip install cocotb
```

---

## Running the Tests

```bash
make
```

The `Makefile` uses cocotb's built-in make rules. It will:

1. Compile `flip_flop.sv` with Icarus Verilog.
2. Run all tests defined in `test_flip_flop.py` in the order specified by `COCOTB_TESTS`.
3. Write results to `results.xml`.

---

### `reset_dut(dut, duration_ns=10)`

Asserts `rst=1` and `d=0`, waits for the timer to expire, synchronises to a rising clock edge, then releases reset and waits one further clock cycle for the DUT to settle. Two assertions are checked before returning:

- `dut.rst.value == 0` — confirms reset was released successfully.
- `dut.q.value == 0` — confirms the DUT output is in its reset state.

### Test cases

Tests run in the following order as defined in the Makefile:

| Order | Test                   | What it checks                                              |
| ----- | ---------------------- | ----------------------------------------------------------- |
| 1     | `test_reset`           | `q` is driven to `0` while `rst=1`, regardless of `d`       |
| 2     | `test_d_captures_high` | `q` captures `d=1` on the next rising clock edge            |
| 3     | `test_d_release_low`   | `q` captures `d=0` on a subsequent rising clock edge        |
| 4     | `test_d_mid_cycle`     | `q` holds its value when `d` changes between clock edges    |
| 5     | `test_toggle_sequence` | `q` correctly tracks an 8-cycle pattern `[1,0,1,1,0,0,1,0]` |

Each test samples `q` 1 ns after the rising clock edge to allow for propagation delay before asserting.

---
