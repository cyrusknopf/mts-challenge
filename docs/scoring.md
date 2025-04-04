# Scoring

_Deciding "how well" a player has performed in a round_

- Motivating a change
  - High variance in scores
  - Scores too dependant on problem setup
    - Getting a long timeframe, high budget means a player can get a high score
      with a poor strategy
    - Diversification scores will be necessarily low with a very restrictive
      client

## Method One: Exploiting Ratios

### Motivation

- Use a weighted sum of **ratios** to calculate score, e.g:

  - Favour returns (profit/budget) over budget
  - Use (industries invested in/client-approved industries) instead of
    industries invested in
    ...

- Ratios can account for factors in problem setup

  - Don't reward players for making large absolute profit (but meagre returns)
    for high budget clients
  - Don't give the same diversification score to players who's clients are
    who have invested in the same number of industries where one has a
    restrictive client and one has a permissive one.

- Points returned from the function will naturally be low variance (in terms
  of scale)

### Maths

- Express points as some weighted sum

$$
\text{points} = \alpha\cdot \text{returns} + \beta\cdot \text{diversification} +
\gamma\cdot \text{client satisfaction}
$$

Returns are calculated conventionally, probably in the range [-0.25, +0.25]

$$
\text{returns} = \frac{\text{profit}}{\text{budget}}
$$

Diversification is calculated looking at the number of industries invested in,
and the range of companies invested in. Crucially, the number of industries that
the client is willing to invest in is taken into account. This is done to
prevent players being penalised for having restrictive clients, or unfairly
rewarded for having permissive clients.

Only liked industries contribute towards diversification scores. This shouldn't
make a difference for well behaved players, but will stop rule-breaking players
from offsetting their losses in client satisfaction here.

(without the todo) this will be in the range [0, 1]

$$
\text{diversification} = \frac{\text{industries invested intersect client likes}}{\text{client-approved
industries}} % TODO: factor in number of stocks bought in a way that doesn't
             % skew towards high-budget clients; not sure how to just yet
$$

Client satisfaction is calculated as a function of the client's risk tolerance
and the riskiness of the portfolio provided. Every percentage point that a
player goes above the client's risk tolerance will result in losses to client
satisfaction.

If a player invests in a disliked industry, **this score will be zero**

Client satisfaction is in the range [0, 1]

$$
\text{client satisfaction} = 1 - \min \left(0, \frac{\text{portfolio risk - client risk
tolerance}}{\text{client risk tolerance}}\right)
$$

## Method Two: ~~Clipping by Difficulty~~

### Motivation

- Assigning a maximum score for each round solves the scaling problem, but

  - Doesn't fix the context problem: makes it easier for players with richer
    clients to get high scores
  - Incentivises players to spam request new clients

- To address both issues:

  - Assign each client a **difficulty** rating, and then assign a max score
    based on the difficulty rating

- Clients become easier with
  - Longer timeframes
  - Larger budgets
  - Fewer dislikes

> Actually, this doesn't work as there is no trivial way to fit an integer score
> to a _max score_; clipping -> everyone gets max score. Would have to change
> scale, which was what method one was doing anyway
