# Limitations

- providers don't support large stacks, limit to 9 switches in a stack
    - Ex: Gi9/0/1 and Gi1/0/1 pass, Gi10/0/1 fails
- providers don't support line cards
    - Ex: Te2/3/16 fails but Te1/1/3 passes
