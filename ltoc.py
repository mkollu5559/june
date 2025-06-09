def process_landing_to_conform():
    """
    :return: completes moving data from landing to conform
    """
    try:
        logger.info(
            "Started {JOB} at {TIME}".format(
                JOB=JOB_NAME, TIME=datetime.now(timezone.utc)
            )
        )
        logger.info(f"processing data for timestamp {incr_ingest_timestamp}")

        job_details = {}
        job_list_with_claim_master_n = []

        with open("config.json") as json_file:
            for i in json_file:
                job_dict = json.loads(i)

                # ✅ Build the list dynamically exactly as you want
                if job_dict.get("Claim_Master", "").strip().upper() == "N":
                    job_list_with_claim_master_n.append(job_dict["Job_Name"].lower())

                # ✅ Keep your original line untouched
                if job_dict["Job_Name"] == JOB_NAME:
                    job_details = job_dict

        # ✅ Drop-in replacement for the original hardcoded list check
        if JOB_NAME.lower() in job_list_with_claim_master_n:
            logger.info("Exiting job {0} as it is marked Claim_Master='N'".format(JOB_NAME))
            return None

        logger.info("job details: {0}".format(job_details))

        if len(job_details) != 0:
            if upd_record_count == "0":
                no_records_received(job_details)
                return

            SourceSchema = json.loads(job_details["Source_Data_Object_Schema_Text"])
            TargetSchema = json.loads(job_details["Target_Data_Object_Schema_Text"])
            schema_details = parse_schema(SourceSchema, TargetSchema)

            if JOB_NAME.lower().find("master") == -1:  # master word not found
                logger.info("History Job")
                crawler_prefixes = ["crawler_history_"]
                crawlers = [
                    JOB_NAME.replace("job_gov_conform_", prefix)
                    for prefix in crawler_prefixes
                ]
            else:
                logger.info("Master Job")

            if JOB_NAME in inventory_job_names:
                crawlers.append("crawler_metadata_awsjobexecution")

            ends_with = ".json" if JOB_NAME in inventory_job_names else ".parquet"

            common_util.update_job_table(
                job_details,
                datetime.now(timezone.utc),
                0,
                0,
                "Started",
                "",
                "",
                datetime.now(timezone.utc),
                JOB_RUN_ID,
                {},
                BUCKET_NAME,
                glue_context,
                spark,
                refresh_type=refresh_type,
            )

            logger.info(f"received refresh type: {refresh_type}")

    except Exception as ex:
        raise Exception("Exception while processing landing to conform") from ex
