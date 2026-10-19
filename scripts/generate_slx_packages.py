"""generate_slx_packages.py

Assembles valid Simulink SLX packages (Open Packaging Conventions zip archives)
for the three required models:
1. Hybrid_OpAmp_Integral.slx
2. Hybrid_OpAmp_Differential.slx
3. Hybrid_OpAmp_Full.slx
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
    <P Name="Location">[100, 100, 1024, 768]</P>
  </Window>
</WindowsInfo>
"""

CORE_PROPERTIES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{title}</dc:title>
  <dc:creator>Senior Analog IC &amp; SET Device Design Engineer</dc:creator>
  <cp:lastModifiedBy>Antigravity MATLAB Automation</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">2026-10-19T18:00:00Z</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">2026-10-19T18:00:00Z</dcterms:modified>
</cp:coreProperties>
"""

MWCORE_PROPERTIES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<mwcoreProperties xmlns="http://schemas.mathworks.com/package/coreProperties">
  <contentType>application/vnd.mathworks.simulink.model</contentType>
</mwcoreProperties>
"""

INTEGRAL_BLOCKDIAGRAM_XML = """<?xml version="1.0" encoding="utf-8"?>
<ModelInformation Version="1.0">
  <Model>
    <P Name="SavedCharacterEncoding">UTF-8</P>
    <P Name="Name">Hybrid_OpAmp_Integral</P>
    <P Name="Version">10.7</P>
    <P Name="Solver">ode23t</P>
    <P Name="StopTime">0.001</P>
    <P Name="RelTol">1e-5</P>
    <P Name="AbsTol">1e-6</P>
    <System>
      <P Name="Location">[100, 100, 1100, 700]</P>
      <P Name="Open">on</P>
      <!-- Block 1: External Vin Inport -->
      <Block BlockType="Inport" Name="Vin_ext" SID="1">
        <P Name="Position">[40, 100, 70, 114]</P>
        <P Name="Port">1</P>
      </Block>
      <!-- Block 2: Test Step Generator -->
      <Block BlockType="Step" Name="Test_Step" SID="2">
        <P Name="Position">[40, 150, 70, 170]</P>
        <P Name="Time">0.0001</P>
        <P Name="Before">0</P>
        <P Name="After">0.01</P>
      </Block>
      <!-- Block 3: Test Sine Wave Generator -->
      <Block BlockType="Sin" Name="Test_Sine" SID="3">
        <P Name="Position">[40, 200, 70, 220]</P>
        <P Name="Amplitude">0.005</P>
        <P Name="Frequency">6283.1853</P>
      </Block>
      <!-- Block 4: Input Signal Switch -->
      <Block BlockType="Switch" Name="Input_Switch" SID="4">
        <P Name="Position">[130, 150, 160, 185]</P>
        <P Name="Criteria">u2 &gt; Threshold</P>
        <P Name="Threshold">0.5</P>
      </Block>
      <!-- Block 5: Driver Transconductance (gm2 = 40 uS) -->
      <Block BlockType="Gain" Name="gm2_Driver" SID="5">
        <P Name="Position">[250, 125, 310, 155]</P>
        <P Name="Gain">40.0e-6</P>
      </Block>
      <!-- Block 6: Intermediate KCL Summing Junction -->
      <Block BlockType="Sum" Name="KCL_Sum" SID="6">
        <P Name="Position">[370, 125, 395, 165]</P>
        <P Name="Inputs">+-</P>
      </Block>
      <!-- Block 7: Miller Integrator (1 / (Cc * s)) -->
      <Block BlockType="Integrator" Name="Miller_Integrator" SID="7">
        <P Name="Position">[450, 125, 490, 165]</P>
        <P Name="InitialCondition">0.4</P>
        <P Name="LimitOutput">on</P>
        <P Name="UpperSaturationLimit">0.75</P>
        <P Name="LowerSaturationLimit">0.05</P>
      </Block>
      <!-- Block 8: Cc Scale Factor (1 / Cc = 1 / 0.5pF = 2e12) -->
      <Block BlockType="Gain" Name="Cc_Scaling" SID="8">
        <P Name="Position">[530, 130, 590, 160]</P>
        <P Name="Gain">2.0e12</P>
      </Block>
      <!-- Block 9: Dynamic Finite ro2 Feedback (ro2 = 2.0 MOhm) -->
      <Block BlockType="Gain" Name="ro2_Feedback" SID="9">
        <P Name="Position">[450, 220, 510, 250]</P>
        <P Name="Gain">5.0e-7</P>
        <P Name="Orientation">left</P>
      </Block>
      <!-- Block 10: SET Active Load Behavioural conductance -->
      <Block BlockType="Gain" Name="gds_SET_Load" SID="10">
        <P Name="Position">[450, 280, 510, 310]</P>
        <P Name="Gain">1.0e-7</P>
        <P Name="Orientation">left</P>
      </Block>
      <!-- Block 11: Output Outport -->
      <Block BlockType="Outport" Name="Vout" SID="11">
        <P Name="Position">[680, 135, 710, 150]</P>
        <P Name="Port">1</P>
      </Block>
      <!-- Block 12: Scope Monitor -->
      <Block BlockType="Scope" Name="Scope_Transient" SID="12">
        <P Name="Position">[680, 75, 715, 110]</P>
      </Block>
      <!-- Block 13: To Workspace Logger -->
      <Block BlockType="ToWorkspace" Name="Log_Vout" SID="13">
        <P Name="Position">[670, 200, 730, 220]</P>
        <P Name="VariableName">Vout_integral</P>
        <P Name="SaveFormat">Array</P>
      </Block>
      <!-- Connections -->
      <Line>
        <P Name="Src">1#out:1</P>
        <P Name="Dst">5#in:1</P>
      </Line>
      <Line>
        <P Name="Src">5#out:1</P>
        <P Name="Dst">6#in:1</P>
      </Line>
      <Line>
        <P Name="Src">6#out:1</P>
        <P Name="Dst">7#in:1</P>
      </Line>
      <Line>
        <P Name="Src">7#out:1</P>
        <P Name="Dst">8#in:1</P>
      </Line>
      <Line>
        <P Name="Src">8#out:1</P>
        <P Name="Dst">11#in:1</P>
      </Line>
      <Line>
        <P Name="Src">8#out:1</P>
        <P Name="Dst">12#in:1</P>
      </Line>
      <Line>
        <P Name="Src">8#out:1</P>
        <P Name="Dst">13#in:1</P>
      </Line>
      <Line>
        <P Name="Src">8#out:1</P>
        <P Name="Dst">9#in:1</P>
      </Line>
      <Line>
        <P Name="Src">9#out:1</P>
        <P Name="Dst">6#in:2</P>
      </Line>
    </System>
  </Model>
</ModelInformation>
"""

DIFF_BLOCKDIAGRAM_XML = """<?xml version="1.0" encoding="utf-8"?>
<ModelInformation Version="1.0">
  <Model>
    <P Name="SavedCharacterEncoding">UTF-8</P>
    <P Name="Name">Hybrid_OpAmp_Differential</P>
    <P Name="Version">10.7</P>
    <P Name="Solver">ode23t</P>
    <P Name="StopTime">0.002</P>
    <P Name="RelTol">1e-5</P>
    <P Name="AbsTol">1e-6</P>
    <System>
      <P Name="Location">[100, 100, 1100, 700]</P>
      <P Name="Open">on</P>
      <!-- Inputs -->
      <Block BlockType="Inport" Name="Vin_pos" SID="1">
        <P Name="Position">[40, 80, 70, 95]</P>
        <P Name="Port">1</P>
      </Block>
      <Block BlockType="Inport" Name="Vin_neg" SID="2">
        <P Name="Position">[40, 140, 70, 155]</P>
        <P Name="Port">2</P>
      </Block>
      <!-- Differential Extraction -->
      <Block BlockType="Sum" Name="Extract_Vid" SID="3">
        <P Name="Position">[150, 100, 175, 130]</P>
        <P Name="Inputs">+-</P>
      </Block>
      <!-- Common Mode Extraction -->
      <Block BlockType="Sum" Name="Sum_Vicm" SID="4">
        <P Name="Position">[150, 180, 175, 210]</P>
        <P Name="Inputs">++</P>
      </Block>
      <Block BlockType="Gain" Name="Half_Gain" SID="5">
        <P Name="Position">[210, 185, 240, 205]</P>
        <P Name="Gain">0.5</P>
      </Block>
      <!-- Differential Gain Path (Avd1 = gm1 * ro1 = 25uS * 2MOhm = 50 V/V) -->
      <Block BlockType="Gain" Name="Diff_Gain_Avd1" SID="6">
        <P Name="Position">[250, 105, 310, 135]</P>
        <P Name="Gain">50.0</P>
      </Block>
      <!-- Common Mode Path (Avcm1 = -ro1 / (2*Rtail) = -2M / 10M = -0.2 V/V) -->
      <Block BlockType="Constant" Name="Nominal_Vicm" SID="7">
        <P Name="Position">[210, 240, 240, 260]</P>
        <P Name="Value">0.4</P>
      </Block>
      <Block BlockType="Sum" Name="CM_Deviation" SID="8">
        <P Name="Position">[270, 185, 290, 215]</P>
        <P Name="Inputs">+-</P>
      </Block>
      <Block BlockType="Gain" Name="CM_Gain_Avcm1" SID="9">
        <P Name="Position">[330, 190, 390, 220]</P>
        <P Name="Gain">-0.2</P>
      </Block>
      <!-- Output Summing -->
      <Block BlockType="Constant" Name="DC_Quiescent_Out" SID="10">
        <P Name="Position">[330, 50, 360, 70]</P>
        <P Name="Value">0.4</P>
      </Block>
      <Block BlockType="Sum" Name="Sum_Stage1" SID="11">
        <P Name="Position">[430, 105, 455, 145]</P>
        <P Name="Inputs">+++</P>
      </Block>
      <!-- Bandwidth Limiting Pole -->
      <Block BlockType="TransferFcn" Name="Pole_Stage1" SID="12">
        <P Name="Position">[490, 110, 560, 150]</P>
        <P Name="Numerator">[1]</P>
        <P Name="Denominator">[3.183e-9 1]</P>
      </Block>
      <!-- Saturation -->
      <Block BlockType="Saturate" Name="Output_Limiter" SID="13">
        <P Name="Position">[600, 115, 630, 145]</P>
        <P Name="UpperLimit">0.75</P>
        <P Name="LowerLimit">0.05</P>
      </Block>
      <!-- Outport -->
      <Block BlockType="Outport" Name="Vout_diff_stage" SID="14">
        <P Name="Position">[700, 120, 730, 140]</P>
        <P Name="Port">1</P>
      </Block>
      <Block BlockType="Scope" Name="Scope_Diff" SID="15">
        <P Name="Position">[700, 60, 730, 95]</P>
      </Block>
      <!-- Connections -->
      <Line>
        <P Name="Src">1#out:1</P>
        <P Name="Dst">3#in:1</P>
      </Line>
      <Line>
        <P Name="Src">2#out:1</P>
        <P Name="Dst">3#in:2</P>
      </Line>
      <Line>
        <P Name="Src">1#out:1</P>
        <P Name="Dst">4#in:1</P>
      </Line>
      <Line>
        <P Name="Src">2#out:1</P>
        <P Name="Dst">4#in:2</P>
      </Line>
      <Line>
        <P Name="Src">4#out:1</P>
        <P Name="Dst">5#in:1</P>
      </Line>
      <Line>
        <P Name="Src">3#out:1</P>
        <P Name="Dst">6#in:1</P>
      </Line>
      <Line>
        <P Name="Src">5#out:1</P>
        <P Name="Dst">8#in:1</P>
      </Line>
      <Line>
        <P Name="Src">7#out:1</P>
        <P Name="Dst">8#in:2</P>
      </Line>
      <Line>
        <P Name="Src">8#out:1</P>
        <P Name="Dst">9#in:1</P>
      </Line>
      <Line>
        <P Name="Src">10#out:1</P>
        <P Name="Dst">11#in:1</P>
      </Line>
      <Line>
        <P Name="Src">6#out:1</P>
        <P Name="Dst">11#in:2</P>
      </Line>
      <Line>
        <P Name="Src">9#out:1</P>
        <P Name="Dst">11#in:3</P>
      </Line>
      <Line>
        <P Name="Src">11#out:1</P>
        <P Name="Dst">12#in:1</P>
      </Line>
      <Line>
        <P Name="Src">12#out:1</P>
        <P Name="Dst">13#in:1</P>
      </Line>
      <Line>
        <P Name="Src">13#out:1</P>
        <P Name="Dst">14#in:1</P>
      </Line>
      <Line>
        <P Name="Src">13#out:1</P>
        <P Name="Dst">15#in:1</P>
      </Line>
    </System>
  </Model>
</ModelInformation>
"""

FULL_BLOCKDIAGRAM_XML = """<?xml version="1.0" encoding="utf-8"?>
<ModelInformation Version="1.0">
  <Model>
    <P Name="SavedCharacterEncoding">UTF-8</P>
    <P Name="Name">Hybrid_OpAmp_Full</P>
    <P Name="Version">10.7</P>
    <P Name="Solver">ode23t</P>
    <P Name="StopTime">0.002</P>
    <P Name="RelTol">1e-5</P>
    <P Name="AbsTol">1e-6</P>
    <System>
      <P Name="Location">[100, 100, 1200, 750]</P>
      <P Name="Open">on</P>
      <!-- Inputs -->
      <Block BlockType="Inport" Name="Vin_pos" SID="1">
        <P Name="Position">[40, 80, 70, 95]</P>
        <P Name="Port">1</P>
      </Block>
      <Block BlockType="Inport" Name="Vin_neg" SID="2">
        <P Name="Position">[40, 140, 70, 155]</P>
        <P Name="Port">2</P>
      </Block>
      <!-- STAGE 1: Differential Input Pair (Vid -> i_out1 = gm1 * Vid) -->
      <Block BlockType="Sum" Name="Vid_Calc" SID="3">
        <P Name="Position">[130, 100, 155, 130]</P>
        <P Name="Inputs">+-</P>
      </Block>
      <Block BlockType="Gain" Name="gm1_Transconductance" SID="4">
        <P Name="Position">[190, 105, 250, 135]</P>
        <P Name="Gain">25.0e-6</P>
      </Block>
      <Block BlockType="Gain" Name="ro1_Output_Resist" SID="5">
        <P Name="Position">[280, 105, 330, 135]</P>
        <P Name="Gain">2.0e6</P>
      </Block>
      <!-- STAGE 2: Hybrid SET-CMOS Integrating Stage (gm2, Miller Cc, ro2) -->
      <Block BlockType="Gain" Name="gm2_Stage2" SID="6">
        <P Name="Position">[370, 105, 420, 135]</P>
        <P Name="Gain">40.0e-6</P>
      </Block>
      <Block BlockType="Sum" Name="KCL_Stage2" SID="7">
        <P Name="Position">[450, 110, 475, 145]</P>
        <P Name="Inputs">+-</P>
      </Block>
      <Block BlockType="Integrator" Name="Miller_Integrator" SID="8">
        <P Name="Position">[510, 115, 545, 145]</P>
        <P Name="InitialCondition">0.4</P>
        <P Name="LimitOutput">on</P>
        <P Name="UpperSaturationLimit">0.75</P>
        <P Name="LowerSaturationLimit">0.05</P>
      </Block>
      <Block BlockType="Gain" Name="Cc_Inv" SID="9">
        <P Name="Position">[580, 120, 630, 140]</P>
        <P Name="Gain">2.0e12</P>
      </Block>
      <Block BlockType="Gain" Name="go2_Feedback" SID="10">
        <P Name="Position">[520, 185, 570, 205]</P>
        <P Name="Gain">5.0e-7</P>
        <P Name="Orientation">left</P>
      </Block>
      <!-- STAGE 3: CMOS Output Buffer -->
      <Block BlockType="Gain" Name="Buffer_Gain" SID="11">
        <P Name="Position">[670, 120, 720, 140]</P>
        <P Name="Gain">0.96</P>
      </Block>
      <Block BlockType="Saturate" Name="Buffer_Limiter" SID="12">
        <P Name="Position">[750, 115, 780, 145]</P>
        <P Name="UpperLimit">0.75</P>
        <P Name="LowerLimit">0.05</P>
      </Block>
      <!-- Power Monitoring (Static Power = 5.84 uW) -->
      <Block BlockType="Constant" Name="Static_Power_uW" SID="13">
        <P Name="Position">[670, 220, 730, 240]</P>
        <P Name="Value">5.84</P>
      </Block>
      <!-- Outputs -->
      <Block BlockType="Outport" Name="Vout" SID="14">
        <P Name="Position">[840, 120, 870, 140]</P>
        <P Name="Port">1</P>
      </Block>
      <Block BlockType="Outport" Name="Power_uW" SID="15">
        <P Name="Position">[840, 220, 870, 240]</P>
        <P Name="Port">2</P>
      </Block>
      <Block BlockType="Scope" Name="Scope_Full" SID="16">
        <P Name="Position">[840, 65, 875, 100]</P>
      </Block>
      <!-- Connections -->
      <Line>
        <P Name="Src">1#out:1</P>
        <P Name="Dst">3#in:1</P>
      </Line>
      <Line>
        <P Name="Src">2#out:1</P>
        <P Name="Dst">3#in:2</P>
      </Line>
      <Line>
        <P Name="Src">3#out:1</P>
        <P Name="Dst">4#in:1</P>
      </Line>
      <Line>
        <P Name="Src">4#out:1</P>
        <P Name="Dst">5#in:1</P>
      </Line>
      <Line>
        <P Name="Src">5#out:1</P>
        <P Name="Dst">6#in:1</P>
      </Line>
      <Line>
        <P Name="Src">6#out:1</P>
        <P Name="Dst">7#in:1</P>
      </Line>
      <Line>
        <P Name="Src">7#out:1</P>
        <P Name="Dst">8#in:1</P>
      </Line>
      <Line>
        <P Name="Src">8#out:1</P>
        <P Name="Dst">9#in:1</P>
      </Line>
      <Line>
        <P Name="Src">9#out:1</P>
        <P Name="Dst">11#in:1</P>
      </Line>
      <Line>
        <P Name="Src">9#out:1</P>
        <P Name="Dst">10#in:1</P>
      </Line>
      <Line>
        <P Name="Src">10#out:1</P>
        <P Name="Dst">7#in:2</P>
      </Line>
      <Line>
        <P Name="Src">11#out:1</P>
        <P Name="Dst">12#in:1</P>
      </Line>
      <Line>
        <P Name="Src">12#out:1</P>
        <P Name="Dst">14#in:1</P>
      </Line>
      <Line>
        <P Name="Src">12#out:1</P>
        <P Name="Dst">16#in:1</P>
      </Line>
      <Line>
        <P Name="Src">13#out:1</P>
        <P Name="Dst">15#in:1</P>
      </Line>
    </System>
  </Model>
</ModelInformation>
"""

def create_slx(output_file: Path, title: str, blockdiagram_xml: str):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_file, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', CONTENT_TYPES_XML.strip())
        zf.writestr('_rels/.rels', RELS_XML.strip())
        zf.writestr('metadata/coreProperties.xml', CORE_PROPERTIES_XML.format(title=title).strip())
        zf.writestr('metadata/mwcoreProperties.xml', MWCORE_PROPERTIES_XML.strip())
        zf.writestr('simulink/windowsInfo.xml', WINDOWS_INFO_XML.strip())
        zf.writestr('simulink/blockdiagram.xml', blockdiagram_xml.strip())
    print(f"Generated SLX package: {output_file} ({output_file.stat().st_size} bytes)")

def main():
    root = Path(__file__).resolve().parent.parent
    models_dir = root / "models"
    simulink_models_dir = root / "simulink" / "models"

    packages = [
        ("Hybrid_OpAmp_Integral.slx", "Hybrid CMOS-SET Op-Amp Integral Section", INTEGRAL_BLOCKDIAGRAM_XML),
        ("Hybrid_OpAmp_Differential.slx", "Hybrid CMOS-SET Op-Amp Differential Stage", DIFF_BLOCKDIAGRAM_XML),
        ("Hybrid_OpAmp_Full.slx", "Hybrid CMOS-SET Complete Operational Amplifier", FULL_BLOCKDIAGRAM_XML),
    ]

    for fname, title, xml in packages:
        # Create in models/
        p1 = models_dir / fname
        create_slx(p1, title, xml)
        # Also copy/sync into simulink/models/ for maximum compatibility
        p2 = simulink_models_dir / fname
        create_slx(p2, title, xml)

if __name__ == "__main__":
    main()
