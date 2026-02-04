import json
import streamlit as st
from classifier import classify_po

st.set_page_config(page_title="PO Category Classifier", layout="centered")

st.title("PO L1-L2-L3 Classifier")
st.caption("Classify purchase order descriptions into L1/L2/L3 categories.")

po_description = st.text_area(
    "PO Description",
    height=140,
    help="Include item, service, or materials details for best results.",
    placeholder="e.g., Annual maintenance for HVAC systems across HQ campus",
)
supplier = st.text_input(
    "Supplier (optional)",
    help="Use the supplier name to improve classification when relevant.",
    placeholder="e.g., Acme Facilities Inc.",
)
debug_raw = st.toggle("Show raw model response on errors", value=False)

def _normalize_text(value: str) -> str:
    return value.strip()

@st.cache_data(show_spinner=False)
def _classify_cached(description: str, supplier_name: str) -> str:
    return classify_po(description, supplier_name)

po_description = _normalize_text(po_description)
supplier = _normalize_text(supplier)

can_classify = bool(po_description)

if st.button("Classify", disabled=not can_classify):
    if not can_classify:
        st.warning("Please enter a PO description.")
    else:
        with st.spinner("Classifying..."):
            result = _classify_cached(po_description, supplier)

        try:
            parsed = json.loads(result)
            if isinstance(parsed, dict):
                l1 = parsed.get("L1") or parsed.get("l1")
                l2 = parsed.get("L2") or parsed.get("l2")
                l3 = parsed.get("L3") or parsed.get("l3")
                if any([l1, l2, l3]):
                    st.subheader("Summary")
                    st.write(f"L1: {l1 or '-'}")
                    st.write(f"L2: {l2 or '-'}")
                    st.write(f"L3: {l3 or '-'}")
            st.subheader("Full JSON")
            st.json(parsed)
        except Exception:
            st.error("Invalid model response (could not parse JSON).")
            if debug_raw:
                st.text(result)
