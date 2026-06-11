# 03 - Factions & Characters

This is the social pillar. It carries half the midgame on its own and gives meaning to every economic number, because every coin is earned *with* someone and *against* someone else.

---

## Part A - The faction system

### Core principle: three factions in triangular tension

No "free" alliances. Every point gained with one faction must cost something with at least one other. If you can max all three at once, the system is broken and you're back to the parallel-tracks problem. They form a triangle where each vertex structurally conflicts with the other two, but at different intensities.

### The three factions

**The Navy (Maritime Authority)** - safety and legitimacy at the price of freedom.
- Gives: protection from inspections, partial immunity, stable but dull public contracts, the ability to shed Heat by informing on others.
- Costs: every favor to the Navy is a betrayal in the eyes of the Pirates; binds you to keep their watched businesses clean.

**The Pirates (Brotherhood of the Coast)** - profit and power at the price of risk.
- Gives: the most lucrative illicit jobs, rare goods unavailable legally, "alternative" protection (they can lean on people for you).
- Costs: every dealing raises Navy attention; the higher you climb their ranks, the bigger a target you are when the wind changes.

**The Merchant Guild (Trading Company)** - the *ambiguous* vertex. Pure economic interest, neither law nor crime.
- Gives: the best supply chains, wholesale prices, exclusive goods, trade routes.
- Costs: subtle - binds you with contracts and exclusives; if you betray them they have the economic means to ruin you (boycotts, raising your costs, buying out your competitors). They don't care if you're dirty, only if you're *reliable* and profitable.

### The geometry of the triangle (who hates whom, and how much)

This asymmetry is what keeps the system alive:

- **Navy <-> Pirates: direct enemies.** Each point with one heavily subtracts from the other, roughly 1:1. This is the main moral-choice axis, the starkest one.
- **Guild <-> (Navy and Pirates): weak conflict.** Earning with the Guild subtracts little from the other two, because everyone needs trade. This makes the Guild the "cushion" faction you fall back on when you don't want to commit - but precisely because they're convenient, they never give the power spikes that committing hard to Navy or Pirates would.

This asymmetry avoids the perfectly symmetric triangle (where the optimal play is always "stay in the middle"). Here staying middle (Guild) is legitimate but mediocre; committing hard is risky but unlocks the best content. The player must decide how much courage they have.

### Relationship levels and what they unlock

Each faction has a threshold-based reputation scale; each threshold unlocks *qualitatively different* content (not percentage bonuses). Example on the Pirates (the richest):

- **Low (tolerated):** sell you contraband at full price, give minor jobs.
- **Medium (associate):** access to big jobs, better prices, introductions to contacts.
- **High (Brotherhood):** entrust you with a wanted pirate to harbor permanently, give you a ship, involve you in heists that change the island's economy.
- **Max:** you become a reference point yourself; others come to you for trafficking.

Navy mirrors this: from authorized supplier, to trusted supplier with rare inspections, to "untouchable" with near-total immunity - in exchange for being their informant. Guild: from customer, to partner with exclusive contracts, to de-facto shareholder sharing routes and warehouses but demanding absolute commercial loyalty.

### Link to the Heat system

This is where systems truly talk. Navy reputation **modulates** how Heat works:
- High Navy = Heat rises slowly, inspections rare and announced.
- Low/negative Navy = Heat rises fast, inspections drop in by surprise.

So siding with the Pirates doesn't just lower a bar - it makes every illicit action *concretely more dangerous* because you've lost the Navy's shield. Faction choice and risk management become the same system seen from two angles. See `04_heat.md`.

### The moment the triangle explodes

The system peaks when a midgame event forces you to break the equilibrium - makes it impossible to keep a foot in all three camps. The Navy declares a pirate hunt and demands you hand over your contacts; or the Pirates plan a big raid on the port and want you to open the gates. You're forced to *burn* one faction for the others, and that decision redefines the back half of the run. This is the narrative climax that emerges from systems without a scripted linear campaign - the payoff for all the hours spent cultivating relationships.

---

## Part B - The character system

Factions give structure; characters give the reason to care. They are the connector between the abstract systems and emotion.

### Core principle: a character is a relationship, not a quest giver

The classic mistake is reducing characters to mission vending machines. A real character has a relationship that *evolves in both directions*: they can trust you more or less, ask for growing favors, betray you, be betrayed by you, and they remember. The design question is not "what missions does this give?" but "what kind of relationship do I want the player to have with this person, and how does it change over time?"

### The three faction-faces

Each faction has a recurring face with a distinct *type* of relationship:

**The Pirate Captain** - charisma and danger. The one you love and never fully trust. Brings the most lucrative jobs, treats you like a friend, makes you feel part of something. Unreliable by nature: promises and sometimes doesn't deliver, pulls you into bigger things than expected. Relationship evolves toward **complicity** - the more you work together, the more his problems become yours. Climax: choosing whether to cover him at your own cost or save yourself by dumping him.

**The Navy Inspector** - order and menace. Not friendship, a *balance of power*. He knows (or suspects) what you do; you know he's corruptible. A dance of favors, bribes, veiled threats, false courtesies. He's not a stupid enemy - he's smart, and every bribe gives him one more hook on you. Evolves toward either **stable collusion** (you become accomplices, he protects you for a cut) or **open conflict** (treat him badly and he becomes the nemesis actively trying to frame you). Two opposite arcs from the same premise.

**The Guild Representative** - cold and rational. No friendship, no dramatic threats, only *mutual interest*. Treats you well as long as you're useful and reliable; the most transactional of the three, and for that reason the one who knifes you most elegantly if you stop being useful. Arc is **mutual dependence**: binds you with ever-more-exclusive contracts until you realize you depend on her more than she on you. Tension: when a better offer (Pirates, Navy) tempts you to break her contract, knowing she doesn't forgive.

### Recurring minor characters (the fabric of the world)

A handful of minor characters who *return* give the world consistency and generate the micro-stories between big events:
- The broke fisherman, your first loyal customer, easy to grow attached to.
- The rival merchant running a competing business, who works against you (and whom you can sabotage, buy out, or ally with). Note: ties into the Heat "shift the blame" valve in `04_heat.md`.
- The drunk blacksmith who makes the best weapons but is a loose cannon.
- The young deckhand asking for work, whom you can raise into your right hand (or who betrays you after you taught him everything).

### The system underneath: how a relationship evolves

Three things tracked by the system:

1. **Trust** - how much the character trusts *you specifically*, changed by your actions toward him, not toward his faction in general. You can have high Pirate reputation but low trust with the Captain if you've personally cheated him. This distinction between faction reputation and personal trust is what makes characters more than faction thermometers.
2. **Shared history** - the system remembers what you've been through together. Saved him during an inspection? Betrayed him once then patched it up? Implemented simply as **flags on key past events** that modify what the character says and offers. No need for a complex system.
3. **Debts & favors** - an economy parallel to money. When a character owes you a favor, it's a resource you can spend (ask him to cover you, give a discount, intervene). When *you* owe him, it's a debt that will weigh. Gives characters real mechanical weight, not just narrative.

### The thing that makes it memorable: bidirectional betrayal

The design that turns characters from good to unforgettable is making betrayal possible *in both directions with real consequences*. The player can betray them; they can betray the player. When a trusted character sells you to the Navy, or when you must decide whether to sell the pirate captain to save yourself - those are the scenes players retell. But for a betrayal to hurt, a relationship must have been built first. Characters must accumulate history *before* the betrayal moment. Betraying someone you just met does nothing; betraying the partner you spent twenty hours with hurts, and that's where the game wins.

### How it ties to the midgame

Characters are the connector that gives the abstract systems emotional weight. The midgame's triangle-breaking event (Navy demands you hand over the Pirates) doesn't hurt because you lose reputation points - it hurts because it means betraying the captain *you've lived twenty hours with*. Numbers create structure, characters create attachment, and attachment is what turns a strategic decision into one that stays with you.
