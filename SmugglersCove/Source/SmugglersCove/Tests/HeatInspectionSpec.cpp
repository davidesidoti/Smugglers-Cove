// Copyright Epic Games, Inc. All Rights Reserved.

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "Misc/AutomationTest.h"
#include "Heat/HeatConfig.h"
#include "Heat/HeatSubsystem.h"
#include "Tests/HeatInspectionListenerStub.h"

#if WITH_DEV_AUTOMATION_TESTS

BEGIN_DEFINE_SPEC(FHeatInspectionSpec, "SmugglersCove.Heat.Inspections",
	EAutomationTestFlags_ApplicationContextMask | EAutomationTestFlags::ProductFilter)
	UGameInstance* GameInstance = nullptr;
	UHeatSubsystem* Heat = nullptr;
	UHeatConfig* Config = nullptr;
	UHeatInspectionListenerStub* Listener = nullptr;
	const FName Weaponry = FName(TEXT("Weaponry"));
	const FName Market = FName(TEXT("Market"));

	void RaiseGlobalHeatTo20()
	{
		// Severity 40 at neutral conditions -> Weaponry 40, global 40 * 0.5 = 20 (normalized 0.2).
		FHeatActionContext Context;
		Context.Activity = Weaponry;
		Context.BaseSeverity = 40.0f;
		Heat->ApplyIllicitAction(Context);
	}
END_DEFINE_SPEC(FHeatInspectionSpec)

void FHeatInspectionSpec::Define()
{
	BeforeEach([this]()
	{
		Config = NewObject<UHeatConfig>();
		Config->AddToRoot();
		Config->MaxHeat = 100.0f;
		// Decay off: inspection math stays exact while time advances.
		Config->GlobalDecayPerHour = 0.0f;
		Config->ActivityDecayPerHour = 0.0f;
		Config->GlobalBleedFraction = 0.5f;
		Config->GainMultiplierAtMinNavyRep = 1.5f;
		Config->GainMultiplierAtMaxNavyRep = 0.5f;
		Config->DecayMultiplierAtMinNavyRep = 0.5f;
		Config->DecayMultiplierAtMaxNavyRep = 1.5f;
		// Inspection tunables: at global heat 20 (0.2 normalized) and neutral rep,
		// pressure accrues at 10 * 0.2 * 1.0 = 2/hour -> threshold 100 in 50 hours.
		Config->InspectionPressurePerHour = 10.0f;
		Config->InspectionPressureThreshold = 100.0f;
		Config->NavyPressureMultiplierAtMinNavyRep = 1.5f;
		Config->NavyPressureMultiplierAtMaxNavyRep = 0.5f;
		Config->WarningHoursAtMinNavyRep = 0.0f;
		Config->WarningHoursAtMaxNavyRep = 24.0f;
		Config->WarningJitterHours = 0.0f; // deterministic by default; jitter tests opt in

		GameInstance = NewObject<UGameInstance>();
		GameInstance->AddToRoot();
		Heat = NewObject<UHeatSubsystem>(GameInstance);
		Heat->SetConfig(Config);
		Heat->RegisterActivity(Weaponry);
		Heat->RegisterActivity(Market);

		Listener = NewObject<UHeatInspectionListenerStub>();
		Listener->AddToRoot();
		Heat->OnInspectionScheduled.AddDynamic(Listener, &UHeatInspectionListenerStub::HandleScheduled);
		Heat->OnInspectionDue.AddDynamic(Listener, &UHeatInspectionListenerStub::HandleDue);
	});

	AfterEach([this]()
	{
		Listener->RemoveFromRoot();
		GameInstance->RemoveFromRoot();
		Config->RemoveFromRoot();
		Listener = nullptr;
		GameInstance = nullptr;
		Heat = nullptr;
		Config = nullptr;
	});

	Describe("Pressure accrual", [this]()
	{
		It("accrues nothing while global heat is zero", [this]()
		{
			Heat->AdvanceTime(100.0f);
			TestEqual("pressure", Heat->GetInspectionPressureNormalized(), 0.0f);
			TestFalse("pending", Heat->IsInspectionPending());
		});

		It("accrues proportionally to global heat", [this]()
		{
			RaiseGlobalHeatTo20();
			Heat->AdvanceTime(10.0f);
			// 10/h * 0.2 * 1.0 * 10h = 20 -> 0.2 of the threshold
			TestEqual("pressure", Heat->GetInspectionPressureNormalized(), 0.2f);
		});

		It("builds faster under hostile Navy reputation", [this]()
		{
			RaiseGlobalHeatTo20(); // applied at neutral rep so heat stays 20
			Heat->SetFallbackNavyReputation(-1.0f);
			Heat->AdvanceTime(10.0f);
			// 10/h * 0.2 * 1.5 * 10h = 30
			TestEqual("pressure", Heat->GetInspectionPressureNormalized(), 0.3f);
		});

		It("builds slower under trusted Navy reputation", [this]()
		{
			RaiseGlobalHeatTo20();
			Heat->SetFallbackNavyReputation(1.0f);
			Heat->AdvanceTime(10.0f);
			// 10/h * 0.2 * 0.5 * 10h = 10
			TestEqual("pressure", Heat->GetInspectionPressureNormalized(), 0.1f);
		});
	});

	Describe("Scheduling", [this]()
	{
		It("schedules an inspection when pressure crosses the threshold", [this]()
		{
			RaiseGlobalHeatTo20();
			Heat->AdvanceTime(50.0f); // 2/h * 50h = 100 = threshold
			TestTrue("pending", Heat->IsInspectionPending());
			TestEqual("scheduled events", Listener->ScheduledCount, 1);
			TestEqual("pressure reset", Heat->GetInspectionPressureNormalized(), 0.0f);
		});

		It("targets the activity with the highest localized heat", [this]()
		{
			RaiseGlobalHeatTo20(); // Weaponry 40
			FHeatActionContext Context;
			Context.Activity = Market;
			Context.BaseSeverity = 10.0f;
			Heat->ApplyIllicitAction(Context); // Market 10, global 25
			Heat->AdvanceTime(50.0f);
			TestTrue("pending", Heat->IsInspectionPending());
			TestEqual("target", Heat->GetPendingInspection().TargetActivity, Weaponry);
			TestEqual("incriminating heat", Heat->GetPendingInspection().TargetActivityHeat, 40.0f);
		});

		It("pauses pressure accrual while an inspection is pending", [this]()
		{
			RaiseGlobalHeatTo20();
			Heat->SetFallbackNavyReputation(1.0f); // long warning so it stays pending
			Heat->AdvanceTime(100.0f);             // 1/h * 100h -> threshold crossed
			TestTrue("pending", Heat->IsInspectionPending());
			Heat->AdvanceTime(5.0f);
			TestEqual("pressure stays at zero", Heat->GetInspectionPressureNormalized(), 0.0f);
			TestEqual("no second schedule", Listener->ScheduledCount, 1);
		});
	});

	Describe("Warning and due", [this]()
	{
		It("grants the configured warning at trusted reputation", [this]()
		{
			Heat->SetFallbackNavyReputation(1.0f);
			Heat->ForceScheduleInspection(Weaponry);
			TestEqual("warning hours", Heat->GetPendingInspection().WarningHours, 24.0f);
			TestFalse("not due yet", Heat->GetPendingInspection().bDue);
			TestEqual("no due event yet", Listener->DueCount, 0);
		});

		It("is due immediately at hostile reputation (surprise inspection)", [this]()
		{
			Heat->SetFallbackNavyReputation(-1.0f);
			Heat->ForceScheduleInspection(Weaponry);
			TestTrue("due", Heat->GetPendingInspection().bDue);
			TestEqual("scheduled events", Listener->ScheduledCount, 1);
			TestEqual("due events", Listener->DueCount, 1);
		});

		It("counts the warning down and fires due exactly once", [this]()
		{
			Heat->SetFallbackNavyReputation(1.0f);
			Heat->ForceScheduleInspection(Weaponry);
			Heat->AdvanceTime(23.0f);
			TestFalse("not due at 23h", Heat->GetPendingInspection().bDue);
			TestFalse("IsInspectionDue false at 23h", Heat->IsInspectionDue());
			Heat->AdvanceTime(1.0f);
			TestTrue("due at 24h", Heat->GetPendingInspection().bDue);
			TestTrue("IsInspectionDue true at 24h", Heat->IsInspectionDue());
			TestEqual("due fired", Listener->DueCount, 1);
			Heat->AdvanceTime(10.0f);
			TestEqual("due fired only once", Listener->DueCount, 1);
		});

		It("keeps the jitter inside the configured window and reproducible per seed", [this]()
		{
			Config->WarningJitterHours = 2.0f;
			Heat->SetFallbackNavyReputation(1.0f);
			Heat->SetInspectionSeed(42);
			Heat->ForceScheduleInspection(Weaponry);
			const float First = Heat->GetPendingInspection().WarningHours;
			TestTrue("within window", First >= 22.0f && First <= 26.0f);

			Heat->ResolvePendingInspection();
			Heat->SetInspectionSeed(42);
			Heat->ForceScheduleInspection(Weaponry);
			TestEqual("same seed, same warning", Heat->GetPendingInspection().WarningHours, First);
		});
	});

	Describe("Resolution", [this]()
	{
		It("clears the pending inspection and resumes accrual", [this]()
		{
			RaiseGlobalHeatTo20();
			Heat->SetFallbackNavyReputation(0.0f);
			Heat->AdvanceTime(50.0f);
			TestTrue("pending", Heat->IsInspectionPending());
			Heat->ResolvePendingInspection();
			TestFalse("cleared", Heat->IsInspectionPending());
			Heat->AdvanceTime(10.0f);
			TestEqual("accrual resumed", Heat->GetInspectionPressureNormalized(), 0.2f);
		});

		It("refuses to force-schedule while one is already pending", [this]()
		{
			AddExpectedMessage(TEXT("an inspection is already pending"), ELogVerbosity::Warning, EAutomationExpectedMessageFlags::Contains, 1);
			Heat->ForceScheduleInspection(Weaponry);
			Heat->ForceScheduleInspection(Market);
			TestEqual("still the first target", Heat->GetPendingInspection().TargetActivity, Weaponry);
			TestEqual("only one scheduled event", Listener->ScheduledCount, 1);
		});
	});
}

#endif // WITH_DEV_AUTOMATION_TESTS
