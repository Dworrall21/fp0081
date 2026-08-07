# build_cmd_02 (essential)
pub fn build_cmd_02(
    mode: CaptureMode,
    program: &[u8],
    type_info: &SensorTypeInfo,
    key_line: &[u8],
    calibration_frames: u16,
    lines_per_frame: u16,
    subst_value: u8,
    factory_calibration_values: &[u8],
    calib_data: &[u8],
) -> Result<Vec<u8>> {
    let mut chunks = split_chunks(program)?;
    line_update_type_1(
        mode,
        &mut chunks,
        type_info,
        key_line,
        subst_value,
        factory_calibration_values,
        calib_data,
    );

    let req_lines: u16 = if mode == CaptureMode::Calibrate {
        calibration_frames * lines_per_frame + 1
    } else {
        0
    };

    let merged = merge_chunks(&chunks);
    let mut out = Vec::with_capacity(5 + merged.len());
    out.push(0x02);
    out.extend_from_slice(&type_info.bytes_per_line.to_le_bytes());
    out.extend_from_slice(&req_lines.to_le_bytes());
    out.extend_from_slice(&merged);
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::sensor_types::FM_3367_001;

    /// `0x10..=0x17` opcodes whose `b[i+2] > 1` get their third byte
    /// multiplied by `mult`; the address byte (`b[i+1]`) bumps by 1
    /// when `inc_address` is true. Note the loop guard `i + 3 < len`
    /// means the *last* possible triplet only fires when there's at
    /// least one trailing byte beyond it — a quirk we preserve from
    /// upstream.
    #[test]
    fn patch_timeslot_scales_third_byte_and_bumps_addr() {
        // 7-byte input: trailing 0x00 keeps the loop alive so both
        // triplets get rewritten.
        let input = [0x10, 0x05, 0x03, 0x10, 0x07, 0x09, 0x00];
        let out = patch_timeslot_table(&input, true, 2);
        assert_eq!(out[0..3], [0x10, 0x06, 0x06]);
        assert_eq!(out[3..6], [0x10, 0x08, 0x12]);
        assert_eq!(out[6], 0x00);
    }

    /// Demonstrates the upstream quirk: a buffer with *exactly* enough
    /// bytes for two triplets only processes the first.
    #[test]
    fn patch_timeslot_loop_guard_drops_last_triplet() {
        let input = [0x10, 0x05, 0x03, 0x10, 0x07, 0x09];
        let out = patch_timeslot_table(&input, true, 2);
        // First triplet IS rewritten.
        assert_eq!(out[0..3], [0x10, 0x06, 0x06]);
        // Second triplet is NOT — `i + 3 < len(b)` is false when i=3.
        assert_eq!(out[3..6], [0x10, 0x07, 0x09]);
    }

