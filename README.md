# Introduction

The main objective is to analyze the Age of Adquisition of certain words in the Spanish language by using AI models.

# V1 - Batch Generation with OpenAI model

Create a batch to process words (~127.000 different words) from the file *“GPT_estimates_AoA_v1.xlsx”* with a prompt similar to the one described in the file (changed in order to receive an adequate response):

> “La edad de adquisición (AoA) de una palabra se refiere a la edad en la que se aprendió una palabra por primera vez.  
> En concreto, cuándo una persona habría entendido por primera vez esa palabra si alguien la hubiera utilizado delante de ella, incluso cuando aún no la hubiera dicho, leído o escrito.  
> Calcule la edad media de adquisición (AoA) de la palabra {palabra} para un hablante nativo de español.  
>  
> El formato de salida debe ser un objeto JSON:  
> `{AoA: número //AoA de la palabra expresado en años, puede incluir decimales, Word: palabra //string}`”

The AI used in this process is chat **gpt-4o-mini** from OpenAI. The program created generates a file where each line specifies a single request to process with the following format:

```json
{"custom_id": "task-{index}", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "temperature": 0, "response_format": { "type": "json_object"}, "messages": [{ "role": "system",  "content": "prompt" }, {"role": "user","content": "desc"}],}}
```

Where the `“prompt”` is the one previously described and the `“desc”` a json object with the word to be processed in the following format: `{"palabra": ”zumo”}` (where “zumo” will be the word extracted from the database).

The batch file is subdivided into several smaller batch files with a maximum size of 10000 requests in order to process them adequately. Once all the batches have been processed successfully the results are dumped into the file *“Results_not_f_t_v00.xlsx”* and the provisional files to create the batch are eliminated.

# V2 – Correlation measurements OpenAI model

In the same line to V1 the file *“Alonso_2014_SpanishAoA.xlsx"* is processed with a batch in OpenAI (~7900 words). This file already contains the estimated AoA of the words provided by a source unknown to the OpenAI model. The new AoA values are obtained from **gpt-4o-mini** and dumped the in the file *“Results_not_f_t_v01.xlsx”*.
We proceed to calculate the correlation coefficients to estimate how similar the AI’s answers are to the ones found in the database:

- Pearson_Corr: 0.7276691992436427
- Spearman_Corr: 0.787075570973569

These results are adequate, taking into account the model hasn’t been specifically trained for this task.

# V3 – Fine-tuned model
To improve previous correlation results we attempted to create a fine-tuned model. For this purpose, we train a model (**gpt-4o-mini-2024-07-18**) with some of the words in the *“Alonso_2014_SpanishAoA.xlsx"* database.

The training format would be the following:

```json
{"messages": [{ "role": "system", "content": "prompt" }, { "role": "user", "content": "word"}, { "role": "assistant", "content": "aoa"}]}
```

In this case, both the `“aoa”` and the `“word”` would be the AoA and the word extracted from the database respectively (prompt is the same). These lines are used to train the model.

In order to select the words used to train the model we use a pseudo-random number generator  to select (X) words, while the rest of the words and AoA values would be used to test the correlation coefficients. (The files used to train the models have been deleted in the latest versions of the git).

The results obtained after the finetuning are stored in an excel with the correlation values of the original database. In these files we can see the words that haven’t been used in the training from the original database (all the words in the database that don’t appear in the excel have trained the model).

We have used the following number of words (X) to train the model:

| Training words (X)     | 300 words          | 1000 words         | 2000 words         |
|------------------------|--------------------|---------------------|---------------------|
| Pearson Correlation    | 0.855301363        | 0.910181208         | 0.930133            |
| Spearman Correlation   | 0.858508341        | 0.912312162         | 0.929804288         |
| Output File Name       | Results_f_t_corr_300.xlsx | Results_f_t_corr_1000.xlsx | Results_f_t_corr_2000.xlsx |

Out of the 3 options observed in the table only the last finetuned model has been conserved as it has a relatively high correlation. And is the one used in the future.

# V4 – Batch test

Once we obtain the finetuned model we then try to evaluate the initial database, *“GPT_estimates_AoA_v1.xlsx”* , with the new model (trained with 2000 words).

For this purpose, we adapt previously used batch generation to obtain new answer values. However, the request of various petitions is proven to be hard for the model as it has a low accuracy and fails to deliver a meaningful answer often. 

In the file found in the *“middle_files”* folder we can observe the file *“batch_job_mmlu_age_0.jsonl”* with the petitions for the batch and the file *“batch_job_mmlu_age_0_result.jsonl”* with the results straight out of the batch. As we can observe the model doesn’t comprehend what we are asking for in most cases and it has a really low accuracy as it only gives an coherent answer in 1 out 30 petitions. This can be observed in the next excel file *“Results_AoA_f_t_2000.xlsx”*.


# V5 – Thread & individual petition test

As the batch request have proven to be unsuccessful a script has been programmed to deploy threads to evaluate the words in the *“GPT_estimates_AoA_v1.xlsx”* database. This is not only consequence of the batch failure but also the accuracy the server seems to have with individual requests. This is the format of the individual requests:

```json
[{ "role": "system", "content": "prompt" }, { "role": "user", "content": { "palabra": "word" }}]
```

Being `“prompt”` the same and `”word”` the one to obtained from the database.

A couple of files are created to assess the accuracy of this method:
- *“ProvResults_100_words.xlsx”* 
- *“ProvResults_10000_words.xlsx”*

Proving 100% accuracy in terms of not getting an invalid answer. For these tests, 3 threads and 200 threads are used respectively with times to complete the process of 31 seconds in the first and 45 minutes in the second one.

Losing connection to the OpenAI server is possible. In order to solve this problem once a thread encounters any issue it is immediately terminated to facilitate stopping the program and restarting the process once connection is reestablished.

In the background a fail-safe program is working which aims to store all the successful petitions in the file *"middle_files/prov_output_counter.jsonl"* as they arrive.  

In the same way, we store:
- the number of petitions processed in order  
- an array with the ones processed out of order  

These variables are kept even after stopping the process to ensure that it can be continued after from where it has ended.

After 281 minutes in the host’s computer the 500 threads finished successfully and the contents of the provisional file were dumped into an Excel file (*“ProvResults_all_words.xlsx”*) and ordered alphabetically (the threads finish in a different order that the one in the original datasheet and should be ordered alphabetically afterwards).