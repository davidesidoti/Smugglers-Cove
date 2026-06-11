# 01 - Overview & Core Loop

## The pitch

Smuggler's Cove is a first-person, pirate-era shopkeeper sim where you run legitimate island businesses that are secretly a front for smuggling and black-market trade. The fantasy is not "be a pirate" - it is *running a respectable enterprise that is quietly criminal underneath, and managing the tension of not getting caught*. Think the riskmanagement fantasy of money laundering, set in the age of sail.

What makes it work, and what the whole design must protect:

- **The dual track must interlock, not run parallel.** The legal business is not just a separate income stream; it is the *necessary cover* for the illegal one. If the two halves don't feed each other, players will optimize into whichever pays more and ignore the rest. Design rule: legal volume is the screen that lets you hide illegal volume without raising Heat, and steady legal activity actively cools Heat. Every system should reinforce that the two halves are gears in one machine.
- **Tension via a pendulum.** Pure relaxation bores; pure stress exhausts. The game swings between calm (daytime, legal, tidy management) and adrenaline (nighttime deals, surprise inspections, risk of losing everything). That oscillation is the hook.
- **The game must generate stories.** Litmus test for any feature: does it help produce the sentence a player tells a friend? "I ran a shop and made money" = dead. "I was hiding the illegal cannons when a surprise inspection hit, bribed the inspector with my last coins, then found out the pirate captain I worked for had sold me out" = alive. Design toward the second sentence.

## The three pillars

1. **Economic** - businesses, upgrades, prices, supply chains. The base, but exhausts on its own. Detailed in `02_activities.md`.
2. **Social / narrative** - factions and recurring characters. Gives the numbers meaning. Detailed in `03_factions_characters.md`.
3. **Risk** - hiding, bribing, evading: the Heat system. Generates the stories. Detailed in `04_heat.md`.

The game is interesting in proportion to how much these three influence each other *continuously*. A single economic decision (open the weaponry) should have social consequences (Guild respects you more, Navy suspects you) and risk consequences (more Heat). If every action touches all three pillars, the game is rich. If each pillar lives alone, it is poor even with tons of content.

## The day/night rhythm

The phase structure keeps everything legible and maps onto the dual track:

- **Day** - the legal face. Open the businesses, serve normal ships, earn clean money, maintain appearances.
- **Night** - the illicit side. Pirates dock under cover of dark, you run risky exchanges, move contraband, meet contacts in the tavern.
- **Surprise inspections** - can land when least expected, so the player never fully relaxes.

This cycle maps directly onto the legal/illegal dual track and gives the lighting/atmosphere of UE5 something to do.

## First-person consequences

First person makes the *physicality of hiding* the standout moment-to-moment. The strongest set piece is a real-time inspection: an inspector approaches and you must physically move contraband into a false-bottom, cover illegal cannons, douse the forge, hide the ledgers - with not enough time to secure everything. That tension is something a top-down management view cannot deliver. See `04_heat.md`.

The risk of first person is that abstract management becomes tedious (walking to a shelf to change a price is misery). Solution: a **management desk** (a table with maps and ledgers) opens a UI for the abstract stuff (prices, orders, contracts), while only the things that are *fun to do physically* stay manual (serving customers, stocking goods, repairing, hiding).

## The core loop, layered

The moment-to-moment, short loop:
serve legal customers -> earn clean money -> take on an illicit job -> move/hide contraband -> manage the resulting Heat -> repeat.

The medium loop (per in-game day/cycle):
balance clean income against illicit margin -> keep Heat under thresholds -> invest in upgrades and relationships -> survive inspections.

The long loop (the midgame engine, see below):
grow from a shack to a small port -> climb faction ladders -> get forced into the choice that breaks the triangle.

## Keeping the midgame alive (the make-or-break)

Management sims die in the midgame. The cause is mathematical, not content: early decisions matter because resources are scarce; once the player is rich, decisions lose weight and the game is "solved" long before it ends. The golden rule: **keep resources scarce and decisions painful even when the player is rich, by moving the source of scarcity onto a new axis each time.**

The levers, in the order scarcity should shift:

1. **Time & attention, not money.** In first person you can't be in two places at once. Running market + repair + weaponry all needing your physical presence makes *you* the scarce resource. Delegating to NPCs is possible but they're worse than you (they steal, err, draw suspicion). The question shifts from "do I have enough money?" to "what do I give my attention to right now?" - which never resolves.
2. **Risk quality, not quantity.** Midgame illicit jobs get *qualitatively* more dangerous, not just bigger. Not "move 100 crates instead of 10" but "harbor a wanted pirate the Navy is actively hunting; if caught you lose a business, not just pay a fine." You start risking things money can't easily rebuy.
3. **Factions as pressure you can't buy off.** Three factions in mutual tension means pleasing one alienates others - a choice no amount of money solves. Midgame question becomes "who do I side with, and what am I willing to lose?"
4. **Unlocks that change *how* you play, not *how much*.** No "+20% profit" upgrades. Unlock underwater smuggling (new way to move goods past surface inspections), a second port (a logistics chain instead of one point), arming your own ships (trader -> something that can fight). Each is a small new game inside the game.
5. **Events that recompose the world.** World events (faction wars, blockades, a Navy pirate-hunt, a plague spiking medicine prices) must be *connected to your systems*, presenting the bill for decisions you'd deferred, forcing a position you'd been avoiding.

The midgame is alive as long as the player's dominant *question* keeps changing:
- Hours 0-3: "do I have enough money to grow?"
- Hours 3-8: "how do I manage rising risk without getting caught?"
- Hours 8-20: "which factions do I side with, and what do I sacrifice?"
- Hours 20+: "how do I hold together an empire too big to control?"

The midgame dies the moment that question freezes on "I wait for the numbers to go up."

## The single guiding compass

**Constantly move the source of scarcity:** money, then time/attention, then faction reputation, then control over your own empire. Every time the player "solves" one kind of scarcity by getting good, the next bottleneck should already be waiting.
