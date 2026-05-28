---
type: note
topic: systems
subtopic: Rust
created: 2026-01-20
modified: 2026-03-05
tags: [systems, Rust, programming, ownership, memory]
---

# Rust Ownership Model

> Understanding Rust's ownership, borrowing, and lifetime system. The mental model that makes it click.

## The Core Rules

1. **Each value has exactly one owner.**
2. **When the owner goes out of scope, the value is dropped.**
3. **You can have either:** one mutable reference OR any number of immutable references — never both at the same time.

These rules are enforced at compile time. Zero runtime cost.

## Ownership in Practice

```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;           // s1 is MOVED into s2 — s1 is no longer valid
    // println!("{}", s1); // ❌ compile error: value used after move
    println!("{}", s2);    // ✅
}
```

For types that implement `Copy` (integers, booleans, char, tuples of Copy types), assignment copies rather than moves:

```rust
let x = 5;
let y = x;  // x is copied, not moved — both valid
```

## Borrowing

```rust
fn calculate_length(s: &String) -> usize {  // & = immutable reference (borrow)
    s.len()
}  // s goes out of scope but does NOT drop the value — it was only borrowed

fn change(s: &mut String) {  // &mut = mutable borrow
    s.push_str(", world");
}
```

**Key constraint**: you can have one `&mut` OR many `&`, never mixed at the same time in the same scope. This prevents data races at compile time.

## The Mental Model That Clicked

Think of ownership as a baton in a relay race. Only one runner holds the baton. When you pass it (move), you no longer have it. When you borrow it (reference), you give it temporarily, but must get it back before doing anything else with it.

The borrow checker is a static analyser that verifies: does every borrow return the baton before the owner needs it back?

## When It's Painful

- **Self-referential structs** — a struct containing a reference to itself is genuinely hard without `Pin<T>` or `Rc<RefCell<T>>`
- **Graph structures** — multiple ownership is the natural model for graphs; Rust pushes you toward `Rc` (reference counting) or arena allocation
- **Early Rust code** — fighting the borrow checker usually means the design needs rethinking, not the borrow checker

## Related

- [[../../Hubs/Technology-Hub]]
- [[WASM-Use-Cases]] — Rust compiles to WASM cleanly; ownership model means no GC in browser
