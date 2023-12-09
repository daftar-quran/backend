
zip -r users.zip lambdas/users

aws s3 cp users.zip s3://halaka-lambdas/users.zip --profile daftar

rm users.zip