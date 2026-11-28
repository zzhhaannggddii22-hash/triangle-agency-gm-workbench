"""Deterministic preflight contract tests for the Blades solo campaign adapter.

TEST-ONLY reference model; not the Blades engine or production GM runtime.
Fixed dice in the integrated case are fixtures, not random rolls.
Crew-level exposure uses the ordinary team track; there is no bespoke solo track.
Death/return details are deliberately not modeled beyond the campaign's stated
paranoia threshold because those consequences will be discussed when relevant.
"""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field
import unittest


@dataclass
class SoloState:
    cash: int = 2
    pressure: int = 0
    ordinary_traumas: list[str] = field(default_factory=list)
    paranoia_traumas: int = 0
    deaths: int = 0
    crew_heat: int = 0
    wanted: int = 0
    crew_mode: str = "single_operator_uses_team_rules"
    house: str = "small_private_house"
    house_is_crew_base: bool = False
    family_aware_of_death: bool = False
    family_support: str = "ongoing_basic_support_unspecified"
    crew: dict | None = None
    phase: str = "freeplay"
    event_ids: set[str] = field(default_factory=set)
    factions: dict = field(default_factory=lambda: {
        "nearby_observers": {"known": [], "plan": None},
        "distant_syndicate": {"known": [], "plan": None},
    })
    long_project_ticks: int = 0
    whisper_xp: int = 0
    status: str = "TEST_ONLY_NON_CANON"


def apply_once(state: SoloState, event_id: str, action) -> bool:
    if event_id in state.event_ids:
        return False
    action()
    state.event_ids.add(event_id)
    return True


def pay_contract(state: SoloState, event_id: str, reward: int, completed: bool) -> bool:
    if not completed:
        return False
    return apply_once(state, event_id, lambda: setattr(state, "cash", state.cash + reward))


def record_team_exposure(state: SoloState, event_id: str, heat: int, informed_factions=()) -> bool:
    """Apply an already-determined ordinary team Heat result once.

    This helper does not define Heat calculation, reductions, thresholds, or
    Wanted consequences. Those remain governed by Blades v1.3.
    """
    def change():
        state.crew_heat += heat
        for faction_id in informed_factions:
            if faction_id in state.factions:
                state.factions[faction_id]["known"].append(event_id)
    return apply_once(state, event_id, change)


def start_downtime(state: SoloState) -> None:
    state.phase = "downtime_planning"
    for faction in state.factions.values():
        if faction["known"]:
            faction["plan"] = {"basis": list(faction["known"]), "status": "planned"}


def resolve_downtime(state: SoloState, activities: list[str], outcomes: dict[str, str]) -> int:
    state.phase = "downtime_resolution"
    extra_count = max(0, len(activities) - 2)
    if state.cash < extra_count:
        raise ValueError("insufficient cash for additional downtime activities")
    state.cash -= extra_count
    for faction_id, faction in state.factions.items():
        if faction["plan"] is not None:
            faction["plan"]["status"] = outcomes.get(faction_id, "pending")
    state.phase = "freeplay"
    return extra_count


def mark_ordinary_trauma(state: SoloState, condition: str) -> None:
    state.ordinary_traumas.append(condition)
    state.pressure = 0


def register_actual_death(state: SoloState, event_id: str) -> bool:
    """Record only the established consequence: one paranoia trauma per death.

    No resurrection timing, location, injury, gear, pressure, or scene fallout
    is modeled here. At the trauma cap, the campaign-specific result is final death.
    """
    def consequence():
        state.deaths += 1
        state.paranoia_traumas += 1
        if state.paranoia_traumas >= 4:
            state.status = "PERMANENT_DEATH"
    return apply_once(state, event_id, consequence)


def rule_precedence(module=None, system=None, general=None):
    return module if module is not None else system if system is not None else general


def npc_assistance(npc_present: bool, performs_useful_action: bool, willing: bool) -> bool:
    return npc_present and performs_useful_action and willing


class BladesSoloPreflightTests(unittest.TestCase):
    def setUp(self):
        self.state = SoloState()

    def test_starting_personal_cash_is_two_and_no_crew_is_established(self):
        self.assertEqual(self.state.cash, 2)
        self.assertIsNone(self.state.crew)

    def test_personal_house_is_not_a_crew_base(self):
        self.assertEqual(self.state.house, "small_private_house")
        self.assertFalse(self.state.house_is_crew_base)

    def test_unspecified_family_support_does_not_create_cash(self):
        self.assertIn("unspecified", self.state.family_support)
        self.assertEqual(self.state.cash, 2)

    def test_solo_operator_uses_shared_team_exposure_tracks(self):
        self.assertEqual(self.state.crew_mode, "single_operator_uses_team_rules")
        self.assertEqual(self.state.crew_heat, 0)
        self.assertEqual(self.state.wanted, 0)
        self.assertFalse(hasattr(self.state, "personal_exposure"))

    def test_contract_reward_is_paid_once_to_personal_cash(self):
        self.assertTrue(pay_contract(self.state, "job-01", 2, True))
        self.assertFalse(pay_contract(self.state, "job-01", 2, True))
        self.assertEqual(self.state.cash, 4)
        self.assertIsNone(self.state.crew)

    def test_failed_contract_does_not_pay_completion_reward(self):
        self.assertFalse(pay_contract(self.state, "job-02", 3, False))
        self.assertEqual(self.state.cash, 2)

    def test_two_downtime_activities_are_free_and_third_costs_one_coin(self):
        self.state.cash = 4
        self.assertEqual(resolve_downtime(self.state, ["project", "training", "extra"], {}), 1)
        self.assertEqual(self.state.cash, 3)

    def test_unaffordable_extra_downtime_activity_is_rejected(self):
        self.state.cash = 0
        with self.assertRaises(ValueError):
            resolve_downtime(self.state, ["project", "training", "extra"], {})
        self.assertEqual(self.state.cash, 0)

    def test_only_informed_factions_make_downtime_plans(self):
        record_team_exposure(self.state, "witnessed-event", 2, ["nearby_observers"])
        start_downtime(self.state)
        self.assertEqual(self.state.factions["nearby_observers"]["plan"]["status"], "planned")
        self.assertIsNone(self.state.factions["distant_syndicate"]["plan"])

    def test_plan_is_not_treated_as_resolved_result(self):
        record_team_exposure(self.state, "witnessed-event", 2, ["nearby_observers"])
        start_downtime(self.state)
        self.assertEqual(self.state.factions["nearby_observers"]["plan"]["status"], "planned")
        resolve_downtime(self.state, ["project", "research"], {"nearby_observers": "partial"})
        self.assertEqual(self.state.factions["nearby_observers"]["plan"]["status"], "partial")

    def test_unseen_secret_does_not_enter_faction_knowledge(self):
        record_team_exposure(self.state, "secret-event", 0, [])
        self.assertEqual(self.state.factions["nearby_observers"]["known"], [])
        self.assertEqual(self.state.factions["distant_syndicate"]["known"], [])

    def test_same_team_exposure_event_is_not_counted_twice(self):
        record_team_exposure(self.state, "single-event", 2, ["nearby_observers"])
        record_team_exposure(self.state, "single-event", 2, ["nearby_observers"])
        self.assertEqual(self.state.crew_heat, 2)
        self.assertEqual(self.state.factions["nearby_observers"]["known"], ["single-event"])

    def test_ordinary_trauma_is_not_death_and_does_not_add_paranoia(self):
        mark_ordinary_trauma(self.state, "reckless")
        self.assertEqual(self.state.deaths, 0)
        self.assertEqual(self.state.paranoia_traumas, 0)

    def test_actual_death_adds_one_paranoia_once(self):
        self.assertTrue(register_actual_death(self.state, "death-01"))
        self.assertFalse(register_actual_death(self.state, "death-01"))
        self.assertEqual((self.state.deaths, self.state.paranoia_traumas), (1, 1))

    def test_full_paranoia_means_permanent_death(self):
        for i in range(1, 5):
            register_actual_death(self.state, f"death-{i}")
        self.assertEqual(self.state.paranoia_traumas, 4)
        self.assertEqual(self.state.status, "PERMANENT_DEATH")

    def test_npc_presence_alone_does_not_grant_help_bonus(self):
        self.assertFalse(npc_assistance(True, False, True))
        self.assertFalse(npc_assistance(False, True, True))
        self.assertFalse(npc_assistance(True, True, False))
        self.assertTrue(npc_assistance(True, True, True))

    def test_rule_precedence_is_module_then_system_then_general(self):
        self.assertEqual(rule_precedence("module", "system", "general"), "module")
        self.assertEqual(rule_precedence(None, "system", "general"), "system")
        self.assertEqual(rule_precedence(None, None, "general"), "general")

    def test_state_snapshot_preserves_resources_and_information_boundaries(self):
        record_team_exposure(self.state, "known-event", 2, ["nearby_observers"])
        start_downtime(self.state)
        restored = deepcopy(self.state)
        self.assertEqual(restored.cash, self.state.cash)
        self.assertEqual(restored.crew_heat, self.state.crew_heat)
        self.assertEqual(restored.factions, self.state.factions)
        self.assertIsNone(restored.factions["distant_syndicate"]["plan"])
        self.assertIsNone(restored.crew)

    def test_integrated_synthetic_solo_cycle(self):
        # Fixed TEST-ONLY fixture: research d6=5, engagement d6=4, action 2d6=[4, 6].
        research, engagement, action_dice = 5, 4, [4, 6]
        self.assertIn(research, (4, 5))
        self.assertIn(engagement, (4, 5))
        self.assertEqual(max(action_dice), 6)
        pay_contract(self.state, "synthetic-job", 2, True)
        record_team_exposure(self.state, "synthetic-witness", 2, ["nearby_observers"])
        start_downtime(self.state)
        self.state.long_project_ticks = 2
        resolve_downtime(self.state, ["project-step-1", "project-step-2"], {"nearby_observers": "partial"})
        self.assertEqual(self.state.cash, 4)
        self.assertEqual(self.state.crew_heat, 2)
        self.assertEqual(self.state.long_project_ticks, 2)
        self.assertEqual(self.state.factions["nearby_observers"]["plan"]["status"], "partial")
        self.assertIsNone(self.state.factions["distant_syndicate"]["plan"])
        self.assertIsNone(self.state.crew)
        self.assertEqual(self.state.status, "TEST_ONLY_NON_CANON")


if __name__ == "__main__":
    unittest.main(verbosity=2)
