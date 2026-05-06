# Database "schema"

all columns are not null unless specified

## Posts

| Column      | Type                            | Restrictions | Description                |
| ----------- | ------------------------------- | ------------ | -------------------------- |
| `id`        | UUID4 as String                 | Primary      | UUID of the post           |
| `posted_on` | Nanosecond timestamp as Integer |              | Timestamp of post          |
| `content`   | String                          |              | Content of post            |
| `username`  | String                          |              | Username (WILL BE CHANGED) | 

## Replies

| Column      | Type                            | Restrictions | Description                |
| ----------- | ------------------------------- | ------------ | -------------------------- |
| `id`        | UUID4 as String                 | Primary      | UUID of the post           |
| `parent_id` | UUID4 as String                 |              | UUID of the parent post    |
| `posted_on` | Nanosecond timestamp as Integer |              | Timestamp of post          |
| `content`   | String                          |              | Content of post            |
| `username`  | String                          |              | Username (WILL BE CHANGED) | 
