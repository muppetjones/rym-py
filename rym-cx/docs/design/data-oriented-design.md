# Data-oriented Design

## Goals

- Support easy lookup and manipulation of various data.
- Easily define and extend relationships
- Automatically build relationships from a given data source

## Use Cases

1. Given two separate data sources `x` and `y` with definitons `{A, B}` and
    `{B, C}`, respectively, derive the relationship `a_xi => c_yj` when
    `b_xi ==  b_yj`.
2. When updating data source `x`, identify the impact of a change in definition
    `A` or `a_i` for other data sources. For example, if the canonical symbol
    of a gene is changed, indicate all transcripts that may be affected.

## Design Decisions

> [!NOTE]  
> Ultimately, the particular choices made boil down to "Why not?"
> The implementation should be usable, but will not focus on optimization
> or feature maximization... at least not yet. However, usability implies
> both speed and a rich feature set: It will be a fight with my OCD to keep
> this feasible and manageable.

### ECS

The Entity-Component-System pattern is often used in game design due to the
flexibility and modularity provided. The benefits of the system are described
in depth elsewhere.

tl;dr: It just makes sense to me as a starting point.

### Python

Python is not as performant as Rust, Zig, or one of the Cs, but it is brilliant
for flexibility and text manipulation, which are key features needed by this
project. Also, I haven't learned Zig yet, I'm not comfortable enough with Rust,
and I'm not enough of a masochist to do text manipulation in C. Plus, I can
always optimize bits later with cython.

Also, there's not really an ECS option in python, at least, not one that I like.
Both bevy and amythyst for Rust are (somewhat) mature projects that just _felt_
good. The python ECS options that I tried felt clunky.

### Open source, rym-py, package management, etc

So why not contribute to an open-source project? Why put it in rym-py?

This project is currently more of an M^2 effort at the moment. I want to see
if I _can_ implement an ECS in python, but more importantly, can I implement
a _good_ ECS in python. Because of course I _can_, but will it be _useful_?
Can I improve on what's already there? This project will be a sandbox; a TDD
sandbox, but more spikes of concepts. I expect mistakes to be made, but I want
the resolution of those to be a part of the process: How do I fix a problem
while keeping backwards compatibility _and_ avoiding (or at least minimizing)
dead, orphaned, or smelly code? I look forward to the challenge.

As for rem-py: It's my pet project. I put my other useful (if simple) tools in
here, why not this? It'll be it's own implicit namespace, so it won't bloat the
others; plus, I expect this project to utilize the others.

I should also probably switch to uv. I have a uv/hatch pattern that works well,
though I do find some uv decisions annoying (namely how it handles virtual
environments -- of course I prefer my supercilious pattern, and poetry and pdm
let me prefer it more easily). I like pdm/hatch, but uv is a little easier
to manage, especially with workspaces. However, it's not a high priority.
