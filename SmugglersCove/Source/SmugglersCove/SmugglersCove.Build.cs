// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class SmugglersCove : ModuleRules
{
	public SmugglersCove(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"AIModule",
			"StateTreeModule",
			"GameplayStateTreeModule",
			"UMG",
			"Slate"
		});

		PrivateDependencyModuleNames.AddRange(new string[] { });

		PublicIncludePaths.AddRange(new string[] {
			"SmugglersCove",
			"SmugglersCove/Variant_Horror",
			"SmugglersCove/Variant_Horror/UI",
			"SmugglersCove/Variant_Shooter",
			"SmugglersCove/Variant_Shooter/AI",
			"SmugglersCove/Variant_Shooter/UI",
			"SmugglersCove/Variant_Shooter/Weapons"
		});

		// Uncomment if you are using Slate UI
		// PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore" });

		// Uncomment if you are using online features
		// PrivateDependencyModuleNames.Add("OnlineSubsystem");

		// To include OnlineSubsystemSteam, add it to the plugins section in your uproject file with the Enabled attribute set to true
	}
}
