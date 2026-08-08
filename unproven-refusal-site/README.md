# Refusal sites nothing has reached yet

Every place in `gate/` and `src/` that can refuse something needs a test that
reaches it. The `proof` leg of the gate enumerates those places from the source
and fails on any that no test executed.

A site that genuinely cannot be reached yet is admitted here. That is a debt
and not a dispensation: a waiver carries what would retire it, and the register
fails closed in both directions. A waiver on a site a test now reaches is stale
and reds the gate. A waiver naming a site that is not in the tree is dangling
and reds the gate. A waiver with nothing that would retire it reds the gate,
because a debt with no repayment is a permission.

This directory is empty of waivers today. That is the state of the tree and not
a property of it: the leg prints how many it read, so a run cannot be mistaken
for one that had none.

## Writing one

One file per site, any name, and two lines that the leg reads:

    Site: gate/pins.py:210
    Retired-when: the schema milestone gives this branch an input that reaches it

    Then whatever a reader needs: why the site cannot be reached now, what was
    tried, and what would change.

`Site:` is the path and the line of the refusal, as the leg prints it. The line
moves when the file above it changes, so a waiver is expected to be edited
along with the code it waives, and a waiver pointing at a line that is no
longer a refusal site is dangling rather than approximately right.

The last resort is to reach the site instead. Almost every waiver that has ever
been written somewhere was cheaper to retire than to justify.
