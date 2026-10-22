import numpy as np
import pytest
from atlas_rf.model import C0_M_S, estimate_patch, array_positions, array_factor, evaluate_design
from atlas_rf.export_geometry import geometry_spec, export_stl


def test_patch_estimate_is_positive():
    p = estimate_patch(11.7e9, 3.48, 0.762e-3)
    assert p.width_m > 0 and p.length_m > 0
    assert p.free_space_wavelength_m == pytest.approx(C0_M_S/11.7e9)


def test_invalid_patch_parameters_rejected():
    with pytest.raises(ValueError):
        estimate_patch(0, 3.48, 0.762e-3)


def test_array_positions_are_centered_and_count_matches():
    pos = array_positions(4, 4, 0.01, 0.01)
    assert pos.shape == (16, 2)
    assert np.mean(pos[:,0]) == pytest.approx(0)
    assert np.mean(pos[:,1]) == pytest.approx(0)


def test_array_factor_boresight_normalized():
    af = array_factor(4, 4, 11.7e9, 0.01, 0.01, np.array(0.0))
    assert float(af) == pytest.approx(1.0)


def test_evaluation_does_not_fabricate_em_metrics():
    result = evaluate_design(4, 4, 11.7e9, 0.01, 0.01)
    assert result["elements"] == 16
    assert result["s11_db"] is None
    assert result["realized_gain_dbi"] is None
    assert result["front_to_back_db"] is None


def test_stl_export_creates_ascii_mesh(tmp_path):
    spec = geometry_spec(11.7e9, 3.48, 0.762e-3, 35e-6, 4, 4, 0.010)
    out = export_stl(spec, tmp_path/"test.stl")
    data = out.read_text()
    assert data.startswith("solid AtlasRF")
    assert data.rstrip().endswith("endsolid AtlasRF_parametric_concept")


def test_spacing_sweep_returns_labelled_analytical_candidates():
    from atlas_rf.model import spacing_sweep
    candidates = spacing_sweep(4, 4, 11.7e9, [0.4, 0.5, 0.6])
    assert len(candidates) == 3
    assert all(c["status"] == "ANALYTICAL_SWEEP_NOT_EM_VALIDATED" for c in candidates)
    assert all("peak_sidelobe_cut_db" in c for c in candidates)
