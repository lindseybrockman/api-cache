-- copy data from csv
copy recipe (name, prep_time, cook_time, ingredients, instructions) from '/Users/lindseybrockman/git-repos/api-cache/crawlers/all_recipes.csv' delimiter ',' csv;


-- add fake ratings
UPDATE
    recipe
SET
    rating = (select mod(id*round(random()*10)::int, 6))

-- add more fake data
INSERT INTO recipe (name, prep_time, cook_time, ingredients, instructions, rating)
SELECT
    md5(random()::text),
    '10 mins',
    '20 mins',
    r.ingredients,
    md5(random()::text),
    0
FROM
    recipe r;

-- example ingredient/name search
SELECT
    name,
    id,
    prep_time,
    cook_time,
    rating
FROM
    recipe
WHERE
    name like '%chicken%'
    OR ingredients like '%chicken%'
ORDER BY
    rating DESC,
    name
LIMIT 30

-- example time search
SELECT
    name,
    id,
    prep_time,
    cook_time,
    rating
FROM
    recipe
WHERE
    name like '%30%'
    OR ingredients like '%30%'
    OR 30 >= (substring(cook_time from '\d+')::int + substring(prep_time from '\d+')::int)
ORDER BY
    rating DESC,
    name
LIMIT 30
