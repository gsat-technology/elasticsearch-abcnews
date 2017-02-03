###Elasticsearch ABC News

Fetches latest ABC news data which is consumed via API Gateway with Lambda proxy. All news items stored in DynamoDB table and logged to CloudWatch Logs.

CloudWatch Logs streamed to Elasticsearch for analysis.

![alt tag](https://raw.githubusercontent.com/gsat-technology/elasticsearch-abcnews/master/resources/high-level-diagram.png)

####Streaming Data from CloudWatch Logs to Elasticsearch

Note that CloudWatch Logs doesn't really stream to Elasticsearch. In the console, when want a log to _Steam to Elasticsearch_ what really ends up happening is that it creates a Lambda called 'LogsToElasticsearch' (this will appear in your list of lambda functions). This lambda, written in nodejs, makes the necessary HTTP reqeusts to the Elasticsearch cluster.

You might not be able to view this code in the console but you can see it by downloading it ([JQ](https://stedolan.github.io/jq/) is an awesome json processor)

```
curl -o LogsToElasticsearch.zip `aws lambda get-function --function-name elasticsearch-abcnews_LogsToElasticsearch | jq .Code.Location --raw-output`
unzip LogsToElasticsearch.zip
cat index.js
```


####CloudFormation resource notes

Setting up Lambda Log -> Elasticsearch integration is a little trickier to do in CloudFormation than using the console because there's a little bit of behind the scenes setup that AWS does. When setting up in CloudFormation, these are the resources that are explicitly required to make the connection.

#####Log group
Lambdas will of course create their _own_ log group BUT in this case we create the log group first with the **same exact** name as what lambda would have created itself. Why? because lambda only creates the log group on the first invocation and we need the log group to come into existence during the Stack creation so we explicitly create it in the template (this doesn't cause any issues for lambda - it doesn't care and just starts logging to the pre-made log group)

#####Subscription Filter
A subscription filter defines which log events (from a CloudWatch Logs group) gets sent to lambda or kinesis.

#####Lambda Permission
Gives CloudWatch Logs service the permission to invoke the _LogsToElasticsearch_ function. It is this resource that requires the log group for the function to exist beforehand.

#####LogsToElasticsearch Lambda function
This is the lambda function that would otherwise get created automatically if the streaming from CloudWatch Logs to Elasticsearch was configured in the console. I've made a small modification to it so that it uses an environment variable to point to the ES domain.
