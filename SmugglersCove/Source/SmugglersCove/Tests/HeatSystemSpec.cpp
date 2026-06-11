// Copyright Epic Games, Inc. All Rights Reserved.

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "Misc/AutomationTest.h"
#include "Heat/HeatConfig.h"
#include "Heat/HeatSubsystem.h"
#include "Tests/HeatNavyRepStub.h"

#if WITH_DEV_AUTOMATION_TESTS

BEGIN_DEFINE_SPEC(FHeatSystemSpec, "SmugglersCove.Heat",
	EAutomationTestFlags_ApplicationContextMask | EAutomationTestFlags::ProductFilter)
	UGameInstance* GameInstance = nullptr;
	UHeatSubsystem* Heat = nullptr;
	UHeatConfig* Config = nullptr;
	const FName Weaponry = FName(TEXT("Weaponry"));
	const FName Market = FName(TEXT("Market"));

	FHeatActionContext MakeAction(float Severity) const
	{
		FHeatActionContext Context;
		Context.Activity = Weaponry;
		Context.BaseSeverity = Severity;
		return Context;
	}
END_DEFINE_SPEC(FHeatSystemSpec)

void FHeatSystemSpec::Define()
{
	BeforeEach([this]()
	{
		Config = NewObject<UHeatConfig>();
		Config->AddToRoot();
		// Explicit, round-number tunables so every expectation below is exact.
		Config->MaxHeat = 100.0f;
		Config->GlobalDecayPerHour = 1.0f;
		Config->ActivityDecayPerHour = 2.0f;
		Config->GlobalBleedFraction = 0.5f;
		Config->LegalCoolingMultiplier = 1.0f;
		Config->MaxDiscretionGainReduction = 0.75f;
		Config->WitnessGainPerWitness = 0.25f;
		Config->NavyShipNearbyMultiplier = 2.0f;
		Config->GainMultiplierAtMinNavyRep = 1.5f;
		Config->GainMultiplierAtMaxNavyRep = 0.5f;
		Config->DecayMultiplierAtMinNavyRep = 0.5f;
		Config->DecayMultiplierAtMaxNavyRep = 1.5f;

		// Subsystems have ClassWithin = UGameInstance: creating one in the transient
		// package trips an engine ensure, so give it a real GameInstance outer.
		GameInstance = NewObject<UGameInstance>();
		GameInstance->AddToRoot();
		Heat = NewObject<UHeatSubsystem>(GameInstance);
		Heat->SetConfig(Config);
		Heat->RegisterActivity(Weaponry);
		Heat->RegisterActivity(Market);
		// Neutral reputation -> both Navy multipliers are exactly 1 with the symmetric values above.
	});

	AfterEach([this]()
	{
		GameInstance->RemoveFromRoot();
		Config->RemoveFromRoot();
		GameInstance = nullptr;
		Heat = nullptr;
		Config = nullptr;
	});

	Describe("ApplyIllicitAction", [this]()
	{
		It("raises the activity heat by the base severity under neutral conditions", [this]()
		{
			const float Gain = Heat->ApplyIllicitAction(MakeAction(10.0f));
			TestEqual("returned gain", Gain, 10.0f);
			TestEqual("weaponry heat", Heat->GetActivityHeat(Weaponry), 10.0f);
		});

		It("bleeds the configured fraction of the gain into global heat", [this]()
		{
			Heat->ApplyIllicitAction(MakeAction(10.0f));
			TestEqual("global heat", Heat->GetGlobalHeat(), 5.0f);
		});

		It("keeps other activities untouched", [this]()
		{
			Heat->ApplyIllicitAction(MakeAction(10.0f));
			TestEqual("market heat", Heat->GetActivityHeat(Market), 0.0f);
		});

		It("reduces the gain with discretion", [this]()
		{
			FHeatActionContext Context = MakeAction(10.0f);
			Context.Discretion = 1.0f;
			const float Gain = Heat->ApplyIllicitAction(Context);
			// 10 * (1 - 1.0 * 0.75) = 2.5
			TestEqual("fully discreet gain", Gain, 2.5f);
		});

		It("increases the gain per witness", [this]()
		{
			FHeatActionContext Context = MakeAction(10.0f);
			Context.WitnessCount = 2;
			const float Gain = Heat->ApplyIllicitAction(Context);
			// 10 * (1 + 2 * 0.25) = 15
			TestEqual("witnessed gain", Gain, 15.0f);
		});

		It("spikes the gain when a Navy ship is nearby", [this]()
		{
			FHeatActionContext Context = MakeAction(10.0f);
			Context.bNavyShipNearby = true;
			const float Gain = Heat->ApplyIllicitAction(Context);
			TestEqual("navy-witnessed gain", Gain, 20.0f);
		});

		It("clamps activity and global heat to MaxHeat", [this]()
		{
			Heat->ApplyIllicitAction(MakeAction(1000.0f));
			TestEqual("weaponry heat clamped", Heat->GetActivityHeat(Weaponry), 100.0f);
			Heat->ApplyIllicitAction(MakeAction(1000.0f));
			TestEqual("global heat clamped", Heat->GetGlobalHeat(), 100.0f);
		});
	});

	Describe("AdvanceTime", [this]()
	{
		It("decays activity and global heat at the configured hourly rates", [this]()
		{
			Heat->ApplyIllicitAction(MakeAction(10.0f)); // weaponry 10, global 5
			Heat->AdvanceTime(2.0f);
			// weaponry: 10 - 2h * 2/h = 6 ; global: 5 - 2h * 1/h = 3
			TestEqual("weaponry heat after decay", Heat->GetActivityHeat(Weaponry), 6.0f);
			TestEqual("global heat after decay", Heat->GetGlobalHeat(), 3.0f);
		});

		It("never decays below zero", [this]()
		{
			Heat->ApplyIllicitAction(MakeAction(10.0f));
			Heat->AdvanceTime(1000.0f);
			TestEqual("weaponry heat floor", Heat->GetActivityHeat(Weaponry), 0.0f);
			TestEqual("global heat floor", Heat->GetGlobalHeat(), 0.0f);
		});

		It("ignores zero and negative time steps", [this]()
		{
			Heat->ApplyIllicitAction(MakeAction(10.0f));
			Heat->AdvanceTime(0.0f);
			Heat->AdvanceTime(-5.0f);
			TestEqual("weaponry heat unchanged", Heat->GetActivityHeat(Weaponry), 10.0f);
		});
	});

	Describe("ApplyLegalAction", [this]()
	{
		It("cools the activity and bleeds the cooling into global heat", [this]()
		{
			Heat->ApplyIllicitAction(MakeAction(10.0f)); // weaponry 10, global 5
			Heat->ApplyLegalAction(Weaponry, 4.0f);
			TestEqual("weaponry heat after legal action", Heat->GetActivityHeat(Weaponry), 6.0f);
			TestEqual("global heat after legal action", Heat->GetGlobalHeat(), 3.0f);
		});

		It("never cools below zero", [this]()
		{
			Heat->ApplyIllicitAction(MakeAction(10.0f));
			Heat->ApplyLegalAction(Weaponry, 1000.0f);
			TestEqual("weaponry heat floor", Heat->GetActivityHeat(Weaponry), 0.0f);
			TestEqual("global heat floor", Heat->GetGlobalHeat(), 0.0f);
		});

		It("ignores non-positive cleaning power", [this]()
		{
			Heat->ApplyIllicitAction(MakeAction(10.0f));
			Heat->ApplyLegalAction(Weaponry, -4.0f);
			TestEqual("weaponry heat unchanged", Heat->GetActivityHeat(Weaponry), 10.0f);
		});
	});

	Describe("Navy reputation modulation", [this]()
	{
		It("slows heat gain when reputation is high", [this]()
		{
			Heat->SetFallbackNavyReputation(1.0f);
			const float Gain = Heat->ApplyIllicitAction(MakeAction(10.0f));
			TestEqual("trusted-rep gain", Gain, 5.0f);
		});

		It("speeds heat gain when reputation is low", [this]()
		{
			Heat->SetFallbackNavyReputation(-1.0f);
			const float Gain = Heat->ApplyIllicitAction(MakeAction(10.0f));
			TestEqual("hostile-rep gain", Gain, 15.0f);
		});

		It("speeds decay when reputation is high", [this]()
		{
			Heat->ApplyIllicitAction(MakeAction(10.0f)); // applied at neutral rep
			Heat->SetFallbackNavyReputation(1.0f);
			Heat->AdvanceTime(1.0f);
			// 10 - 1h * 2/h * 1.5 = 7
			TestEqual("weaponry heat with fast cooling", Heat->GetActivityHeat(Weaponry), 7.0f);
		});

		It("slows decay when reputation is low", [this]()
		{
			Heat->ApplyIllicitAction(MakeAction(10.0f));
			Heat->SetFallbackNavyReputation(-1.0f);
			Heat->AdvanceTime(1.0f);
			// 10 - 1h * 2/h * 0.5 = 9
			TestEqual("weaponry heat with slow cooling", Heat->GetActivityHeat(Weaponry), 9.0f);
		});

		It("prefers an injected provider over the fallback value", [this]()
		{
			UHeatNavyRepStub* Stub = NewObject<UHeatNavyRepStub>();
			Stub->AddToRoot();
			Stub->NavyReputation = 1.0f;
			Heat->SetFallbackNavyReputation(-1.0f);
			Heat->SetNavyReputationProvider(Stub);
			const float Gain = Heat->ApplyIllicitAction(MakeAction(10.0f));
			TestEqual("provider-driven gain", Gain, 5.0f);
			Stub->RemoveFromRoot();
		});
	});
}

#endif // WITH_DEV_AUTOMATION_TESTS
