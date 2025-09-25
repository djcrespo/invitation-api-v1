# # config/storages.py
# from storages.backends.s3boto3 import S3Boto3Storage

# class StaticStorage(S3Boto3Storage):
#     bucket_name = 'django-static'
#     location = 'static'
#     default_acl = 'public-read'
#     file_overwrite = True

# class MediaStorage(S3Boto3Storage):
#     bucket_name = 'django-media'
#     location = 'media'
#     default_acl = 'private'
#     file_overwrite = False