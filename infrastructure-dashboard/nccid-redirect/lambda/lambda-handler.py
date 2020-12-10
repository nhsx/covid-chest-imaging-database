def handler(event, context):
    return {
        "statusCode": 301,
        "headers": {
            "Location": "https://www.nhsx.nhs.uk/covid-19-response/data-and-covid-19/national-covid-19-chest-imaging-database-nccid/"
        },
    }
