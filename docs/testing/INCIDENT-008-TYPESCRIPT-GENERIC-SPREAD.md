# Incident 008: TypeScript Rejected the Generic Scenario Spread

## Summary

The Phase 5 repository checks passed and Docker reached the React production
build. TypeScript stopped on the generic scenario updater.

## Observed failure

```text
src/App.tsx(263,20): error TS2698:
Spread types may only be created from object types.
```

## Root cause

The updater used a generic key:

```ts
<K extends keyof Scenario>(section: K, values: Partial<Scenario[K]>)
```

and then spread `current[section]`.

Although every current scenario section is an object, TypeScript 7 does not
narrow a generic indexed access to one concrete object shape at that spread
site.

## Resolution

The interface now uses explicit typed updaters:

- `updateSimulation`
- `updateArrivals`
- `updateService`
- `updateQueue`

Each function spreads a statically known object property.

## Prevention

Phase 5 repository verification requires all four typed updaters and rejects:

- the generic `keyof Scenario` updater
- the indexed `[section]` spread

## Impact

No API, scenario contract or UI workflow was removed. The change only makes
the state update boundary explicit and type-safe.
