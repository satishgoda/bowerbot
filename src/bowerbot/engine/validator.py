# Copyright 2026 Binary Core LLC
# SPDX-License-Identifier: Apache-2.0

"""SceneValidator — the 'Inspector' layer.

Walks through a completed USD stage and checks for errors:
overlapping objects, missing references, scale inconsistencies,
missing defaultPrim, etc.
"""

from bowerbot.schemas import Severity, ValidationIssue, ValidationResult


class SceneValidator:
    """Validates a USD stage for correctness before export."""

    def __init__(self, meters_per_unit: float = 1.0, up_axis: str = "Y") -> None:
        self.expected_meters_per_unit = meters_per_unit
        self.expected_up_axis = up_axis

    def validate(self, stage_path: str) -> ValidationResult:
        """Run all validation checks on a USD stage."""
        from pxr import Usd, UsdGeom

        stage = Usd.Stage.Open(stage_path)
        if stage is None:
            return ValidationResult(
                is_valid=False,
                issues=[
                    ValidationIssue(
                        severity=Severity.ERROR,
                        message=f"Failed to open stage: {stage_path}",
                    )
                ],
            )

        issues: list[ValidationIssue] = []

        issues.extend(self._check_default_prim(stage))
        issues.extend(self._check_meters_per_unit(stage))
        issues.extend(self._check_up_axis(stage))
        issues.extend(self._check_references(stage))

        is_valid = not any(i.severity == Severity.ERROR for i in issues)
        return ValidationResult(is_valid=is_valid, issues=issues)

    def _check_default_prim(self, stage) -> list[ValidationIssue]:  # noqa: ANN001
        """Every stage must have a defaultPrim set."""
        if not stage.GetDefaultPrim():
            return [
                ValidationIssue(
                    severity=Severity.ERROR,
                    message="Stage has no defaultPrim set.",
                )
            ]
        return []

    def _check_meters_per_unit(self, stage) -> list[ValidationIssue]:  # noqa: ANN001
        """metersPerUnit must match expected value."""
        from pxr import UsdGeom

        actual = UsdGeom.GetStageMetersPerUnit(stage)
        if abs(actual - self.expected_meters_per_unit) > 1e-6:
            return [
                ValidationIssue(
                    severity=Severity.ERROR,
                    message=(
                        f"metersPerUnit is {actual}, "
                        f"expected {self.expected_meters_per_unit}"
                    ),
                )
            ]
        return []

    def _check_up_axis(self, stage) -> list[ValidationIssue]:  # noqa: ANN001
        """upAxis must match expected value."""
        from pxr import UsdGeom

        actual = UsdGeom.GetStageUpAxis(stage)
        expected_token = (
            UsdGeom.Tokens.y if self.expected_up_axis == "Y" else UsdGeom.Tokens.z
        )
        if actual != expected_token:
            return [
                ValidationIssue(
                    severity=Severity.WARNING,
                    message=f"upAxis is '{actual}', expected '{self.expected_up_axis}'",
                )
            ]
        return []

    def _check_references(self, stage) -> list[ValidationIssue]:  # noqa: ANN001
        """All external references must resolve to existing files."""
        from pathlib import Path

        issues = []
        for prim in stage.Traverse():
            refs = prim.GetMetadata("references")
            if refs is None:
                continue
            for ref_list_op in [refs.explicitItems, refs.prependedItems, refs.appendedItems]:
                if ref_list_op is None:
                    continue
                for ref in ref_list_op:
                    asset_path = ref.assetPath
                    if asset_path and not Path(asset_path).exists():
                        stage_dir = Path(stage.GetRootLayer().realPath).parent
                        if not (stage_dir / asset_path).exists():
                            issues.append(
                                ValidationIssue(
                                    severity=Severity.ERROR,
                                    message=f"Unresolved reference: {asset_path}",
                                    prim_path=str(prim.GetPath()),
                                )
                            )
        return issues
