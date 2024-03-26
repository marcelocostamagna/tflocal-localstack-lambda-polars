provider "aws" {
  region = "us-east-1" # Specify your AWS region
}

resource "aws_s3_bucket" "landing_bucket" {
  bucket = "landing"
  force_destroy = true 
}

resource "aws_s3_bucket" "bronze_bucket" {
  bucket = "bronze" 
  force_destroy = true
}

resource "aws_s3_bucket" "silver_bucket" {
  bucket = "silver" 
  force_destroy = true
}

# Define a bucket for the lambda zip
resource "aws_s3_bucket" "lambda_code_bucket" {
  bucket        = "lambdas"
  force_destroy = true
  lifecycle {
    prevent_destroy = false
  }
}

# Lambda source code for copying from landing to bronze
resource "aws_s3_object" "lambda_code_copy" {
  bucket = aws_s3_bucket.lambda_code_bucket.id
  source = "lambdas/cp-landing-bronze/cp-landing-bronze-package.zip"
  key    = "cp-landing-bronze-package.zip"
}

# Lambda source code for converting to parquet with polars and move to silver bucket
resource "aws_s3_object" "lambda_code_to_parquet" {
  bucket = aws_s3_bucket.lambda_code_bucket.id
  source = "lambdas/convert-parquet-silver/convert-parquet-silver-package.zip"
  key    = "convert-parquet-silver-package.zip"
}

# Lambda definition for copying from landing to bronze
resource "aws_lambda_function" "lambda_cp_s3" {
  function_name = "lambda-cp-landing-bronze"
  handler       = "handler.lambda_handler"
  runtime       = "python3.10"  
  role          = "arn:aws:iam::000000000000:role/lambda-role"
  s3_bucket     = aws_s3_bucket.lambda_code_bucket.id
  s3_key        = aws_s3_object.lambda_code_copy.key
  memory_size   = 512
  timeout       = 60
}

# Lambda definition for converting to parquet with polars and move to silver bucket
resource "aws_lambda_function" "lambda_convert_parquet" {
  function_name = "lambda-convert-parquet"
  handler       = "handler.lambda_handler"
  runtime       = "python3.10"  
  role          = "arn:aws:iam::000000000000:role/lambda-role"
  s3_bucket     = aws_s3_bucket.lambda_code_bucket.id
  s3_key        = aws_s3_object.lambda_code_to_parquet.key
  memory_size   = 512
  timeout       = 60
}


resource "aws_s3_bucket_notification" "event_landing_object_created" {
  bucket = aws_s3_bucket.landing_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.lambda_cp_s3.arn
    events              = ["s3:ObjectCreated:*"]
    # filter_prefix       = "your_prefix" // optional: filter by prefix
  }
}

resource "aws_s3_bucket_notification" "event_bronze_object_created" {
  bucket = aws_s3_bucket.bronze_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.lambda_convert_parquet.arn
    events              = ["s3:ObjectCreated:*"]
  }
}

