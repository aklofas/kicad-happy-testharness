"""Facts shared by the output validators."""

DESIGN_INTENT_REQUIRED = {"product_class", "ipc_class", "target_market",
                          "confidence", "detection_signals", "source"}
PRODUCT_CLASSES = {"prototype", "production"}
IPC_CLASSES = {1, 2, 3}
TARGET_MARKETS = {"hobby", "consumer", "industrial", "medical",
                  "automotive", "aerospace"}


def pcb_output_name(schematic_output_name):
    """PCB output file name paired with a schematic output name, or None."""
    if schematic_output_name.endswith(".kicad_sch.json"):
        return schematic_output_name.replace(".kicad_sch.json", ".kicad_pcb.json")
    if schematic_output_name.endswith(".sch.json"):
        return schematic_output_name.replace(".sch.json", ".kicad_pcb.json")
    return None
