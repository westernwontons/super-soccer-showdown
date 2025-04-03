# Super Soccer Showdown

The Star Wars and Pokemon universes have collided and a big soccer tournament is being planned to
settle which universe is best.

The application generates random teams for each universe.

# Requirements

1. Each team must consist of 5 players
2. Each player can only play one position
3. Each player has three stats:

    - name
    - weight
    - height

4. Each team has three different player types:

    - goalie (tallest player)
    - defence (heaviest player)
    - offence (shortest player)

5. Each team can be configured with different lineups (the number of attackers and defenders)

# Stretch goals

1. https://pokeapi.co has been really unstable lately. How can you ensure your service can deliver
   even during times of instability?
2. A spambot has found your service! How can you ensure only people are using your service?
3. Our SuperSoccer Showdown has gone viral! How can we handle all of these users?
4. We want to show the 'soccer team power' which is the sum of a new statistic 'player soccer
   power', how can we support this?
5. Write a function that given two teams, simulates a match and returns a list of highlights e.g.
   "Pikachu scored against Han Solo".

# Project structure

## Models

The `models` module defines the `Player` and `Team` data types. A `Team` consists of a collection of
`Player`s, where is one goalie and a mix of attackers and/or defenders. A `Team` consists of at most
5 `Player`s. Since the goalie takes one slot, _4_ is left for attackers/defenders. This means that a
`Team`, where there is one goalie and 4 attackers is perfectly valid, so is one with 4 defenders or
2 attackers and 2 defenders.

## Providers

The `providers` module exports the `PlayerProvider`. Implementors of this protocol generate a pool
of `Player`s ready to be assembled into a team

## Assembler

The `assembler` module exports the `TeamAssembler`, which takes an arbitrary list of `Player`s and
produces a `Team` that's guaranteed to be valid.

A `Team`s validity is determined by the collection of `Player`s it holds. The assembler makes sure
that a team:

    - has 5 players
    - has 1 goalie and that the goalie is the tallest player out of the team
    - has at most 4 attackers and/or defenders and each attacker or defender is the heaviest or the shortest in their team

# Deployment

The project is ready to be deployed to `fly.io`. A `fly.toml` configuration file is included:

    - Download [flyctl](https://fly.io/docs/flyctl/install)
    - Authenticate your account
    - Run `fly deploy`

Since the project is developed with [FastAPI](https://fastapi.tiangolo.com), using
[uvicorn](https://www.uvicorn.org/) would allow to have multiple instances of the application.
However, in it's current state, since there's no database and all the players reside in memory, each
instance would have it's own copy of the players and each instance would also fetch the same data
for all the APIs used. The data is read-only, so this is acceptable.

With multiple instances, a load-balancer would be appropriate to sit in front of the instances.
However, `fly.io` has [Fly Proxy](https://fly.io/docs/reference/fly-proxy) which handles this.
Furthermore, `fly.io` allows spinning up multiple instances of the application easily, making the
usage of uvicorn a little redundant. My recommendation would be to use either/or but not both.
Unless this is unsuitable, `nginx`, `caddy` or `envoy` (or any other load-balancer) would work if a
more manual solution is needed.

The application is publicly available at `https://super-soccer-showdown.fly.dev`.

# Adding other universes

The current structure of the application makes it very easy to add another universe. The first step
should be to subclass the `ApiClient` ABC and implement the necessary logic to fetch players from
wherever. After that, an implementation of `PlayerProvider` should be underway to allow
_provisioning_ potential players. To include this in the HTTP API, it is recommended to add this new
universe to the `TeamAssemblerService` and add an HTTP handler for building a team out of the
players for that universe.
