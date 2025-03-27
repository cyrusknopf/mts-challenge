# PRISM

```
 ________________
 /_______________/\
 \ \            / /
  \ \    ______/_/_______
   \ \  /\______________/\
 ___\ \_\_\__/ /_      / /
/\___\ \____/ /__\    / /
\ \   \ \ \ \/ / /   / /
 \ \   \ \/\ \/ /   / /
  \ \   \/_/\/ /   / /
   \ \      / /\  / /
    \ \    / /\ \/ /
     \ \  / /  \_\/
      \ \/ /
       \/_/
```


## Logistical Considerations
- Generation and distribution of API keys to teams on the day
  - Write a quick script to add an API key to the database, including setting name, columns, etc.

- Stress test of the system overall

- Stress test of the evaluation function
  - Generate a lot of suitable portfolios, run through evaluation function

- Evaluate suitability of the evaluation function
  - Manually check a few portfolios, see if we like the results

- Server:
    - HTTP
    - API Keys

## TODOs

- [ ] Baseline Python app for teams to get started
- [ ] Attempt to host on GCP
- [ ] Attempt to host on GCP




# Docker instructions
`docker compose up --build -d`
`docker compose exec prism-server bash`
- Gemini is free
