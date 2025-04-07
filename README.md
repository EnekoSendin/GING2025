# V1 - Batch Generation with OpenAI model

Create a batch to process words (~127.000 different words) from the file “GPT_estimates_AoA_v1.xlsx” with a prompt similar to the one described in the file (changed in order to receive an adequate response):

> “La edad de adquisición (AoA) de una palabra se refiere a la edad en la que se aprendió una palabra por primera vez.  
> En concreto, cuándo una persona habría entendido por primera vez esa palabra si alguien la hubiera utilizado delante de ella, incluso cuando aún no la hubiera dicho, leído o escrito.  
> Calcule la edad media de adquisición (AoA) de la palabra {palabra} para un hablante nativo de español.  
>  
> El formato de salida debe ser un objeto JSON:  
> `{AoA: número //AoA de la palabra expresado en años, puede incluir decimales, Word: palabra //string}`”

The AI used in this process is chat gpt-4o-mini. The program created generates a file where each line specifies a single request to process with the following format:

```json
{"custom_id": f"task-{index}", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "temperature": 0, "response_format": { "type": "json_object"}, "messages": [{ "role": "system",  "content": prompt }, {"role": "user","content": desc}],}}
```

Where the “prompt” is the one previously described and the “desc” a json object with the word to be processed in the following format: `{"palabra": ”zumo”}` (where “zumo” will be the word extracted from the database).

The batch file is subdivided into several smaller batch files with a maximum size of 10000 requests in order to process them adequately. Once all the batches have been processed successfully the results are dumped into the file “Results_not_f_t_v00.xlsx” and the provisional files to create the batch are eliminated.

...

# V5 – Thread & individual petition test

As the batch request have proven to be unsuccessful a script has been programmed to deploy threads to evaluate the words in the “GPT_estimates_AoA_v1.xlsx” database. This is not only consequence of the batch failure but also the accuracy the server seems to have with individual requests. This is the format of the individual requests:

```json
[{ "role": "system", "content": prompt }, { "role": "user", "content": { "palabra": word }}]
```

Being “prompt” the same and ”word” the one to obtained from the database.

A couple of files are created to assess the accuracy of this method:
- “ProvResults_100_words.xlsx”  
- “ProvResults_10000_words.xlsx”

Proving 100% accuracy in terms of not getting an invalid answer. For these tests, 3 threads and 200 threads are used respectively with times to complete the process of 31 seconds in the first and 45 minutes in the second one.

Losing connection to the OpenAI server is possible. In order to solve this problem once a thread encounters any issue it is immediately terminated to facilitate stopping the program and restarting the process once connection is reestablished.

In the background a fail-safe program is working which aims to store all the successful petitions in the file:
- `middle_files/prov_output_counter.jsonl` as they arrive.  

In the same way, we store:
- the number of petitions processed in order  
- an array with the ones processed out of order  

These variables are kept even after stopping the process to ensure that it can be continued after from where it has ended.

After 281 minutes in the host’s computer the 500 threads finished successfully and the contents of the provisional file were dumped into an Excel file (“ProvResults_all_words.xlsx”) and ordered alphabetically (the threads finish in a different order that the one in the original datasheet and should be ordered alphabetically afterwards).