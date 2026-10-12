# Example session: emoji gesture filter

> **Placeholder.** This file is a structural stand-in awaiting a real session
> transcript. It is written to show the shape the file should take, and it has
> not been captured from a working session. Replace the body below with an
> actual transcript, then remove this notice.
>
> The intended source is the author's own experience learning computer vision
> by building an emoji gesture filter, which is the project that motivated
> this skill. A real transcript is worth more here than a polished one, so
> keep the wrong turns and the stuck moments.

## Project

An emoji gesture filter. A webcam captures frames, a hand-landmark model
returns coordinates, and a rule decides which emoji to draw based on the
shape of the hand.

## Why this project is a good example

It is a natural fit for the arc. The naive version is a set of hardcoded
thresholds comparing landmark positions, which works for the hand that wrote
it and degrades for everyone else. That failure is the moment the project
becomes a lesson in why a trained classifier earns its place.

## The blueprint

```
webcam frame -> hand landmarks -> rule -> emoji -> canvas
```

Twenty-one landmarks per hand, each an `(x, y, z)` triple, normalized to the
`0.0`-`1.0` range of the input frame rather than expressed in pixels.

## The slices

_To be filled from the real session._

## The break

The point at which the hardcoded threshold failed on real input, what the
landmark data actually looked like at that moment, and what the user
concluded. This is the part worth keeping verbatim.

## The upgrade

Whether the fix was a trained classifier, a better rule, or an explanation
that no upgrade was needed, and why.
