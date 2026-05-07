# Database "schema"
all columns are not null

## Posts

| Column      | Type                            | Restrictions                           | Description                |
| ----------- | ------------------------------- | -------------------------------------- | -------------------------- |
| `id`        | UUID4 as String                 | Primary                                | UUID of the post           |
| `posted_on` | Nanosecond timestamp as Integer |                                        | Timestamp of post          |
| `content`   | String                          |                                        | Content of post            |
| `user_id`   | UUID4 as String                 | Foreign key (Users), Cascade deletions | UUID of poster             |

## Replies

| Column      | Type                            | Restrictions                           | Description                |
| ----------- | ------------------------------- | -------------------------------------- | -------------------------- |
| `id`        | UUID4 as String                 | Primary                                | UUID of the post           |
| `parent_id` | UUID4 as String                 | Foreign key (Posts), Cascade deletions | UUID of the parent post    |
| `posted_on` | Nanosecond timestamp as Integer |                                        | Timestamp of post          |
| `content`   | String                          |                                        | Content of post            |
| `user_id`   | UUID4 as String                 | Foreign key (Users), Cascade deletions | UUID of poster             | 

## Users

| Column          | Type                            | Restrictions | Description                           |
| --------------- | ------------------------------- | ------------ | ------------------------------------- |
| `user_id`       | UUID4 as String                 | Primary      | UUID of user                          |
| `creation_ts`   | Nanosecond timestamp as Integer |              | Timestamp of account creation         |
| `username`      | String                          | Unique       | Username of account                   |
| `token_version` | Integer                         |              | Password version (for JWT revocation) |
