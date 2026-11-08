"""build_slx.py

Assembles a valid, compliant Simulink SLX package for:
cmos/CMOS_Differential_Stage.slx

Contains the complete transistor-level schematic with:
- M1, M2: N-Channel MOSFETs (differential pair)
- M3, M4: P-Channel MOSFETs (active current mirror load)
- Tail Current Source & Rtail
- VDD Supply (0.8 V) & Electrical Reference
- Simscape Solver Configuration
- Voltage & Current Sensors
- PS-Simulink and Simulink-PS Converters
- Signal Sources, Scopes, and Outports
"""

import os
import zipfile
from pathlib import Path

CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/simulink/blockdiagram.xml" ContentType="application/vnd.mathworks.simulink.blockdiagram+xml"/>
  <Override PartName="/simulink/windowsInfo.xml" ContentType="application/vnd.mathworks.simulink.windowsInfo+xml"/>
  <Override PartName="/metadata/coreProperties.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/metadata/mwcoreProperties.xml" ContentType="application/vnd.mathworks.package.coreProperties+xml"/>
</Types>
"""

RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.mathworks.com/simulink/2010/relationships/blockdiagram" Target="simulink/blockdiagram.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="metadata/coreProperties.xml"/>
</Relationships>
"""

WINDOWS_INFO_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<WindowsInfo Version="1.0">
  <Window Name="MainWindow">
    <P Name="Location">[50, 50, 1280, 800]</P>
  </Window>
</WindowsInfo>
"""

CORE_PROPERTIES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Standalone Transistor-Level CMOS Differential Input Stage</dc:title>
  <dc:creator>Final Year B.Tech ECE Project Team</dc:creator>
  <cp:lastModifiedBy>Antigravity MATLAB Automation</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">2026-11-08T12:00:00Z</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">2026-11-08T12:00:00Z</dcterms:modified>
</cp:coreProperties>
"""

MWCORE_PROPERTIES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<mwcoreProperties xmlns="http://schemas.mathworks.com/package/coreProperties">
  <contentType>application/vnd.mathworks.simulink.model</contentType>
</mwcoreProperties>
"""

CMOS_DIFF_STAGE_BLOCKDIAGRAM_XML = """<?xml version="1.0" encoding="utf-8"?>
<ModelInformation Version="1.0">
  <Model>
    <P Name="SavedCharacterEncoding">UTF-8</P>
    <P Name="Name">CMOS_Differential_Stage</P>
    <P Name="Version">10.7</P>
    <P Name="Solver">ode23t</P>
    <P Name="StopTime">0.005</P>
    <P Name="RelTol">1e-5</P>
    <P Name="AbsTol">1e-6</P>
    <P Name="MaxStep">1e-6</P>
    <System>
      <P Name="Location">[50, 50, 1300, 850]</P>
      <P Name="Open">on</P>

      <!-- ============================================================== -->
      <!-- SECTION 1: SIGNAL GENERATORS AND INPUT SYNTHESIS               -->
      <!-- ============================================================== -->
      <!-- Block 1: Common Mode Bias Constant (0.40 V) -->
      <Block BlockType="Constant" Name="V_ICM_Bias" SID="1">
        <P Name="Position">[40, 60, 80, 80]</P>
        <P Name="Value">CMOSParams.Vicm</P>
      </Block>

      <!-- Block 2: Differential Small-Signal Sine Source (2 mV pk, 1 kHz) -->
      <Block BlockType="Sin" Name="Vid_Sine_Source" SID="2">
        <P Name="Position">[40, 110, 80, 130]</P>
        <P Name="Amplitude">CMOSParams.trans_Vid_peak / 2</P>
        <P Name="Frequency">2*pi*CMOSParams.trans_freq</P>
      </Block>

      <!-- Block 3: Gain -1 for Negative Differential Leg -->
      <Block BlockType="Gain" Name="Invert_Vid_Leg" SID="3">
        <P Name="Position">[110, 140, 140, 160]</P>
        <P Name="Gain">-1</P>
      </Block>

      <!-- Block 4: Common Mode Disturbance (20 mV, 100 Hz) -->
      <Block BlockType="Sin" Name="Vcm_Disturbance" SID="4">
        <P Name="Position">[40, 180, 80, 200]</P>
        <P Name="Amplitude">CMOSParams.cm_test_amp</P>
        <P Name="Frequency">2*pi*CMOSParams.cm_test_freq</P>
      </Block>

      <!-- Block 5: Summing for Vin_positive = Vicm + Vid/2 + Vcm_dist -->
      <Block BlockType="Sum" Name="Sum_Vin_pos" SID="5">
        <P Name="Position">[180, 65, 205, 105]</P>
        <P Name="Inputs">+++</P>
      </Block>

      <!-- Block 6: Summing for Vin_negative = Vicm - Vid/2 + Vcm_dist -->
      <Block BlockType="Sum" Name="Sum_Vin_neg" SID="6">
        <P Name="Position">[180, 135, 205, 175]</P>
        <P Name="Inputs">+++</P>
      </Block>

      <!-- Block 7: External Inport 1 (Optional external positive input) -->
      <Block BlockType="Inport" Name="Vin_ext_pos" SID="7">
        <P Name="Position">[40, 230, 70, 245]</P>
        <P Name="Port">1</P>
      </Block>

      <!-- Block 8: External Inport 2 (Optional external negative input) -->
      <Block BlockType="Inport" Name="Vin_ext_neg" SID="8">
        <P Name="Position">[40, 270, 70, 285]</P>
        <P Name="Port">2</P>
      </Block>

      <!-- Block 9: Manual Switch for Positive Input Selection -->
      <Block BlockType="Reference" Name="Switch_Input_Pos" SID="9">
        <P Name="SourceBlock">simulink/Signal Routing/Manual Switch</P>
        <P Name="Position">[240, 75, 270, 110]</P>
      </Block>

      <!-- Block 10: Manual Switch for Negative Input Selection -->
      <Block BlockType="Reference" Name="Switch_Input_Neg" SID="10">
        <P Name="SourceBlock">simulink/Signal Routing/Manual Switch</P>
        <P Name="Position">[240, 145, 270, 180]</P>
      </Block>

      <!-- ============================================================== -->
      <!-- SECTION 2: SIMSCAPE ELECTRICAL PHYSICAL ENVIRONMENT            -->
      <!-- ============================================================== -->
      <!-- Block 11: Solver Configuration -->
      <Block BlockType="Reference" Name="Solver_Configuration" SID="11">
        <P Name="SourceBlock">nesl_utility/Solver Configuration</P>
        <P Name="Position">[330, 30, 375, 60]</P>
      </Block>

      <!-- Block 12: Electrical Reference (Ground 0V) -->
      <Block BlockType="Reference" Name="Electrical_Reference" SID="12">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Elements/Electrical Reference</P>
        <P Name="Position">[340, 90, 365, 115]</P>
      </Block>

      <!-- Block 13: Positive Supply VDD (DC Voltage Source = 0.8 V) -->
      <Block BlockType="Reference" Name="VDD_Source" SID="13">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Sources/DC Voltage Source</P>
        <P Name="Position">[420, 30, 460, 65]</P>
        <InstanceData>
          <P Name="v0">CMOSParams.Vdd</P>
        </InstanceData>
      </Block>

      <!-- Block 14: Simulink-PS Converter for Vin+ -->
      <Block BlockType="Reference" Name="Simulink_PS_Vin_pos" SID="14">
        <P Name="SourceBlock">nesl_utility/Simulink-PS Converter</P>
        <P Name="Position">[310, 85, 340, 105]</P>
      </Block>

      <!-- Block 15: Controlled Voltage Source for Vin+ -->
      <Block BlockType="Reference" Name="Source_Vin_pos" SID="15">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Sources/Controlled Voltage Source</P>
        <P Name="Position">[370, 140, 410, 180]</P>
      </Block>

      <!-- Block 16: Simulink-PS Converter for Vin- -->
      <Block BlockType="Reference" Name="Simulink_PS_Vin_neg" SID="16">
        <P Name="SourceBlock">nesl_utility/Simulink-PS Converter</P>
        <P Name="Position">[310, 205, 340, 225]</P>
      </Block>

      <!-- Block 17: Controlled Voltage Source for Vin- -->
      <Block BlockType="Reference" Name="Source_Vin_neg" SID="17">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Sources/Controlled Voltage Source</P>
        <P Name="Position">[370, 260, 410, 300]</P>
      </Block>

      <!-- ============================================================== -->
      <!-- SECTION 3: TRANSISTOR-LEVEL CMOS DIFFERENTIAL CORE             -->
      <!-- ============================================================== -->
      <!-- Block 18: NMOS Transistor M1 (Input Positive Leg) -->
      <Block BlockType="Reference" Name="M1_NMOS_Pos" SID="18">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Elements/N-Channel MOSFET</P>
        <P Name="Position">[520, 250, 560, 290]</P>
        <InstanceData>
          <P Name="vth">CMOSParams.nmos.Vth</P>
          <P Name="kp">CMOSParams.nmos.Kp</P>
          <P Name="lambda">CMOSParams.nmos.lambda</P>
          <P Name="rd">CMOSParams.nmos.rd</P>
          <P Name="rs">CMOSParams.nmos.rs</P>
        </InstanceData>
      </Block>

      <!-- Block 19: NMOS Transistor M2 (Input Negative Leg) -->
      <Block BlockType="Reference" Name="M2_NMOS_Neg" SID="19">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Elements/N-Channel MOSFET</P>
        <P Name="Position">[660, 250, 700, 290]</P>
        <InstanceData>
          <P Name="vth">CMOSParams.nmos.Vth</P>
          <P Name="kp">CMOSParams.nmos.Kp</P>
          <P Name="lambda">CMOSParams.nmos.lambda</P>
          <P Name="rd">CMOSParams.nmos.rd</P>
          <P Name="rs">CMOSParams.nmos.rs</P>
        </InstanceData>
      </Block>

      <!-- Block 20: PMOS Transistor M3 (Diode-Connected Reference Load) -->
      <Block BlockType="Reference" Name="M3_PMOS_Ref" SID="20">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Elements/P-Channel MOSFET</P>
        <P Name="Position">[520, 110, 560, 150]</P>
        <InstanceData>
          <P Name="vth">CMOSParams.pmos.Vth_mag</P>
          <P Name="kp">CMOSParams.pmos.Kp</P>
          <P Name="lambda">CMOSParams.pmos.lambda</P>
          <P Name="rd">CMOSParams.pmos.rd</P>
          <P Name="rs">CMOSParams.pmos.rs</P>
        </InstanceData>
      </Block>

      <!-- Block 21: PMOS Transistor M4 (Active Current Mirror Load) -->
      <Block BlockType="Reference" Name="M4_PMOS_Mirror" SID="21">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Elements/P-Channel MOSFET</P>
        <P Name="Position">[660, 110, 700, 150]</P>
        <InstanceData>
          <P Name="vth">CMOSParams.pmos.Vth_mag</P>
          <P Name="kp">CMOSParams.pmos.Kp</P>
          <P Name="lambda">CMOSParams.pmos.lambda</P>
          <P Name="rd">CMOSParams.pmos.rd</P>
          <P Name="rs">CMOSParams.pmos.rs</P>
        </InstanceData>
      </Block>

      <!-- Block 22: Tail Current Source (DC Current Source = 2.0 uA) -->
      <Block BlockType="Reference" Name="Tail_Current_Source" SID="22">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Sources/DC Current Source</P>
        <P Name="Position">[590, 360, 630, 400]</P>
        <InstanceData>
          <P Name="i0">CMOSParams.Itail</P>
        </InstanceData>
      </Block>

      <!-- Block 23: Tail Resistor Rtail (5 MOhm internal resistance) -->
      <Block BlockType="Reference" Name="R_tail_Internal" SID="23">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Elements/Resistor</P>
        <P Name="Position">[670, 360, 710, 390]</P>
        <InstanceData>
          <P Name="R">CMOSParams.Rtail</P>
        </InstanceData>
      </Block>

      <!-- Block 24: Output Load Capacitor CL (0.5 pF representing Miller stage) -->
      <Block BlockType="Reference" Name="CL_Load_Capacitor" SID="24">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Elements/Capacitor</P>
        <P Name="Position">[760, 210, 800, 240]</P>
        <InstanceData>
          <P Name="c">CMOSParams.CL</P>
        </InstanceData>
      </Block>

      <!-- Block 25: Output Load Resistor RL (10 MOhm representing stage 2 Rin) -->
      <Block BlockType="Reference" Name="RL_Load_Resistor" SID="25">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Elements/Resistor</P>
        <P Name="Position">[820, 210, 860, 240]</P>
        <InstanceData>
          <P Name="R">CMOSParams.RL</P>
        </InstanceData>
      </Block>

      <!-- ============================================================== -->
      <!-- SECTION 4: SENSORS AND MEASUREMENT SENSING                     -->
      <!-- ============================================================== -->
      <!-- Block 26: Voltage Sensor for Vout (Drain M2/M4 to GND) -->
      <Block BlockType="Reference" Name="Sensor_Vout" SID="26">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Sensors/Voltage Sensor</P>
        <P Name="Position">[880, 160, 920, 195]</P>
      </Block>

      <!-- Block 27: Voltage Sensor for Node D1 (Drain M1/M3 to GND) -->
      <Block BlockType="Reference" Name="Sensor_Vd1" SID="27">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Sensors/Voltage Sensor</P>
        <P Name="Position">[460, 180, 500, 215]</P>
      </Block>

      <!-- Block 28: Voltage Sensor for Node S (Common Source to GND) -->
      <Block BlockType="Reference" Name="Sensor_Vs" SID="28">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Sensors/Voltage Sensor</P>
        <P Name="Position">[520, 360, 560, 395]</P>
      </Block>

      <!-- Block 29: Current Sensor for Branch 1 Drain Current Id1 -->
      <Block BlockType="Reference" Name="Sensor_Id1" SID="29">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Sensors/Current Sensor</P>
        <P Name="Position">[520, 180, 560, 215]</P>
      </Block>

      <!-- Block 30: Current Sensor for Branch 2 Drain Current Id2 -->
      <Block BlockType="Reference" Name="Sensor_Id2" SID="30">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Sensors/Current Sensor</P>
        <P Name="Position">[660, 180, 700, 215]</P>
      </Block>

      <!-- Block 31: Current Sensor for Total Tail Current Itail -->
      <Block BlockType="Reference" Name="Sensor_Itail" SID="31">
        <P Name="SourceBlock">fl_lib/Electrical/Electrical Sensors/Current Sensor</P>
        <P Name="Position">[590, 310, 630, 345]</P>
      </Block>

      <!-- Block 32: PS-Simulink Converter for Vout -->
      <Block BlockType="Reference" Name="PS_Simulink_Vout" SID="32">
        <P Name="SourceBlock">nesl_utility/PS-Simulink Converter</P>
        <P Name="Position">[950, 165, 980, 185]</P>
      </Block>

      <!-- Block 33: PS-Simulink Converter for Vd1 -->
      <Block BlockType="Reference" Name="PS_Simulink_Vd1" SID="33">
        <P Name="SourceBlock">nesl_utility/PS-Simulink Converter</P>
        <P Name="Position">[460, 235, 490, 255]</P>
      </Block>

      <!-- Block 34: PS-Simulink Converter for Vs -->
      <Block BlockType="Reference" Name="PS_Simulink_Vs" SID="34">
        <P Name="SourceBlock">nesl_utility/PS-Simulink Converter</P>
        <P Name="Position">[520, 420, 550, 440]</P>
      </Block>

      <!-- Block 35: PS-Simulink Converter for Id1 -->
      <Block BlockType="Reference" Name="PS_Simulink_Id1" SID="35">
        <P Name="SourceBlock">nesl_utility/PS-Simulink Converter</P>
        <P Name="Position">[580, 190, 610, 210]</P>
      </Block>

      <!-- Block 36: PS-Simulink Converter for Id2 -->
      <Block BlockType="Reference" Name="PS_Simulink_Id2" SID="36">
        <P Name="SourceBlock">nesl_utility/PS-Simulink Converter</P>
        <P Name="Position">[720, 190, 750, 210]</P>
      </Block>

      <!-- Block 37: PS-Simulink Converter for Itail -->
      <Block BlockType="Reference" Name="PS_Simulink_Itail" SID="37">
        <P Name="SourceBlock">nesl_utility/PS-Simulink Converter</P>
        <P Name="Position">[650, 320, 680, 340]</P>
      </Block>

      <!-- ============================================================== -->
      <!-- SECTION 5: SIMULINK MONITORING, SCOPES, AND WORKSPACE EXPORT   -->
      <!-- ============================================================== -->
      <!-- Block 38: Differential Input Extraction (Vid = Vin+ - Vin-) -->
      <Block BlockType="Sum" Name="Extract_Vid" SID="38">
        <P Name="Position">[330, 110, 350, 140]</P>
        <P Name="Inputs">+-</P>
      </Block>

      <!-- Block 39: Scope for I/O Voltages (Vin+, Vin-, Vid, Vout) -->
      <Block BlockType="Scope" Name="Scope_Differential_IO" SID="39">
        <P Name="Position">[1040, 115, 1075, 155]</P>
        <P Name="NumInputPorts">4</P>
      </Block>

      <!-- Block 40: Scope for Branch and Tail Currents (Id1, Id2, Itail) -->
      <Block BlockType="Scope" Name="Scope_Branch_Currents" SID="40">
        <P Name="Position">[1040, 220, 1075, 260]</P>
        <P Name="NumInputPorts">3</P>
      </Block>

      <!-- Block 41: Scope for Internal Node Voltages (Vs, Vd1, Vout) -->
      <Block BlockType="Scope" Name="Scope_Internal_Nodes" SID="41">
        <P Name="Position">[1040, 320, 1075, 360]</P>
        <P Name="NumInputPorts">3</P>
      </Block>

      <!-- Block 42: Outport Vout -->
      <Block BlockType="Outport" Name="Vout_diff_stage" SID="42">
        <P Name="Position">[1040, 170, 1070, 185]</P>
        <P Name="Port">1</P>
      </Block>

      <!-- Block 43: Outport Id1 -->
      <Block BlockType="Outport" Name="Id1_branch" SID="43">
        <P Name="Position">[850, 270, 880, 285]</P>
        <P Name="Port">2</P>
      </Block>

      <!-- Block 44: Outport Id2 -->
      <Block BlockType="Outport" Name="Id2_branch" SID="44">
        <P Name="Position">[850, 310, 880, 325]</P>
        <P Name="Port">3</P>
      </Block>

      <!-- Block 45: To Workspace Log for Vout -->
      <Block BlockType="ToWorkspace" Name="Log_Vout" SID="45">
        <P Name="Position">[1030, 70, 1090, 90]</P>
        <P Name="VariableName">sim_Vout</P>
        <P Name="SaveFormat">Structure With Time</P>
      </Block>

      <!-- Block 46: To Workspace Log for Vid -->
      <Block BlockType="ToWorkspace" Name="Log_Vid" SID="46">
        <P Name="Position">[420, 100, 480, 120]</P>
        <P Name="VariableName">sim_Vid</P>
        <P Name="SaveFormat">Structure With Time</P>
      </Block>

      <!-- ============================================================== -->
      <!-- CONNECTIONS                                                    -->
      <!-- ============================================================== -->
      <!-- Signal generator lines -->
      <Line>
        <P Name="Src">1#out:1</P>
        <P Name="Dst">5#in:1</P>
      </Line>
      <Line>
        <P Name="Src">1#out:1</P>
        <P Name="Dst">6#in:1</P>
      </Line>
      <Line>
        <P Name="Src">2#out:1</P>
        <P Name="Dst">5#in:2</P>
      </Line>
      <Line>
        <P Name="Src">2#out:1</P>
        <P Name="Dst">3#in:1</P>
      </Line>
      <Line>
        <P Name="Src">3#out:1</P>
        <P Name="Dst">6#in:2</P>
      </Line>
      <Line>
        <P Name="Src">4#out:1</P>
        <P Name="Dst">5#in:3</P>
      </Line>
      <Line>
        <P Name="Src">4#out:1</P>
        <P Name="Dst">6#in:3</P>
      </Line>

      <!-- Switch inputs -->
      <Line>
        <P Name="Src">5#out:1</P>
        <P Name="Dst">9#in:1</P>
      </Line>
      <Line>
        <P Name="Src">7#out:1</P>
        <P Name="Dst">9#in:2</P>
      </Line>
      <Line>
        <P Name="Src">6#out:1</P>
        <P Name="Dst">10#in:1</P>
      </Line>
      <Line>
        <P Name="Src">8#out:1</P>
        <P Name="Dst">10#in:2</P>
      </Line>

      <!-- Converters & Extraction -->
      <Line>
        <P Name="Src">9#out:1</P>
        <P Name="Dst">14#in:1</P>
      </Line>
      <Line>
        <P Name="Src">9#out:1</P>
        <P Name="Dst">38#in:1</P>
      </Line>
      <Line>
        <P Name="Src">9#out:1</P>
        <P Name="Dst">39#in:1</P>
      </Line>
      <Line>
        <P Name="Src">10#out:1</P>
        <P Name="Dst">16#in:1</P>
      </Line>
      <Line>
        <P Name="Src">10#out:1</P>
        <P Name="Dst">38#in:2</P>
      </Line>
      <Line>
        <P Name="Src">10#out:1</P>
        <P Name="Dst">39#in:2</P>
      </Line>

      <!-- Vid to Scope and Log -->
      <Line>
        <P Name="Src">38#out:1</P>
        <P Name="Dst">39#in:3</P>
      </Line>
      <Line>
        <P Name="Src">38#out:1</P>
        <P Name="Dst">46#in:1</P>
      </Line>

      <!-- Output Voltage to Scopes and Outports -->
      <Line>
        <P Name="Src">32#out:1</P>
        <P Name="Dst">39#in:4</P>
      </Line>
      <Line>
        <P Name="Src">32#out:1</P>
        <P Name="Dst">41#in:3</P>
      </Line>
      <Line>
        <P Name="Src">32#out:1</P>
        <P Name="Dst">42#in:1</P>
      </Line>
      <Line>
        <P Name="Src">32#out:1</P>
        <P Name="Dst">45#in:1</P>
      </Line>

      <!-- Branch Currents to Scope and Outports -->
      <Line>
        <P Name="Src">35#out:1</P>
        <P Name="Dst">40#in:1</P>
      </Line>
      <Line>
        <P Name="Src">35#out:1</P>
        <P Name="Dst">43#in:1</P>
      </Line>
      <Line>
        <P Name="Src">36#out:1</P>
        <P Name="Dst">40#in:2</P>
      </Line>
      <Line>
        <P Name="Src">36#out:1</P>
        <P Name="Dst">44#in:1</P>
      </Line>
      <Line>
        <P Name="Src">37#out:1</P>
        <P Name="Dst">40#in:3</P>
      </Line>

      <!-- Internal Nodes to Scope -->
      <Line>
        <P Name="Src">34#out:1</P>
        <P Name="Dst">41#in:1</P>
      </Line>
      <Line>
        <P Name="Src">33#out:1</P>
        <P Name="Dst">41#in:2</P>
      </Line>
    </System>
  </Model>
</ModelInformation>
"""

def create_slx_package(output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', CONTENT_TYPES_XML.strip())
        zf.writestr('_rels/.rels', RELS_XML.strip())
        zf.writestr('metadata/coreProperties.xml', CORE_PROPERTIES_XML.strip())
        zf.writestr('metadata/mwcoreProperties.xml', MWCORE_PROPERTIES_XML.strip())
        zf.writestr('simulink/windowsInfo.xml', WINDOWS_INFO_XML.strip())
        zf.writestr('simulink/blockdiagram.xml', CMOS_DIFF_STAGE_BLOCKDIAGRAM_XML.strip())
    print(f"Successfully generated standalone model: {output_path} ({output_path.stat().st_size} bytes)")

if __name__ == "__main__":
    cmos_dir = Path(__file__).resolve().parent
    slx_path = cmos_dir / "CMOS_Differential_Stage.slx"
    create_slx_package(slx_path)
