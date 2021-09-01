import cloudinary
from cloudinary import uploader


# def upload_to_s3(key, data, complete_file=False):
#     session = Session(aws_access_key_id=keysInformation['aws.accessKey'],
#                       aws_secret_access_key=keysInformation['aws.secretKey'],
#                       region_name=keysInformation["s3.region"]).resource('s3').Bucket(keysInformation["s3.bucket"])
#     if complete_file:
#         session.upload_file(data, key)
#     else:
#         session.put_object(Key=key, Body=data)


def upload_to_s3(key, data, complete_file=False):
    CLOUD_NAME = "mollify"
    API_KEY = "466423759736745"
    API_SECRET = "Arv-iXxAZuNrVgf3k4_nS47VFag"

    cloudinary.config(
        cloud_name=CLOUD_NAME,
        api_key=API_KEY,
        api_secret=API_SECRET
    )
    result_ = cloudinary.uploader.upload_large_part(data)
    cloudinary.logger.info("######## FILE UPLOADED TO CLOUDINARY AND SECURE URL IS {} ##################".format(
        result_.get("secure_url")))
    return result_.get("secure_url")
