# crowdstrike_int

```

John is a talented research engineer who dedicates most of his time analyzing clean and malware files. Besides reverse engineering of executables, John make use of several applications and services to analyze the behavior of these files. Because we are proudly part of the Cloud Department, we decided to create a service that would enable him to analyze the behavior of a file in relation to other files. As such, this service will store information about a given file and how it links to other files. 
A file is described by the following metadata: Id (String) 
      •	Name (String)
      •	Platform (String)
      •	Date Added (DateTime as ISO 8601 string) 
A file can be linked to another file by any combination of the following three relationships: 
      •	A downloaded B – if file A downloaded file B from the Internet
      •	A executed B – if file A executed file B on the system
      •	A removed B – if file A deleted file B on the system 
Requirements 
1.	(20p) Use Swagger to define a REST API that would offer the following functionality: 
1.	(5p) Add metadata about a file and its relationships to other files in the system 
2.	(5p) Update the metadata of a file, including relationships to other files 
3.	(5p) View metadata about a file, including relationships to other files 
4.	(5p) Delete file metadata on the system, including relationships to other files 

2.	(40p) From Swagger generate a Python/Go/Java server and implement the functionality of the REST API, using a Redis database for storage. 
3.	(40p) Extend the API to offer the following features: 


1.	(10p) Given a file, list all files that downloaded/executed/deleted it 
2.	(15p) Given a platform, a type (executor/downloader/remover), a date and a limit, list the most 
recent <limit> files that are <type> on that platform added since the given date 
3.	(15p) Given two files, list the first chain of files and relationships found that would link the two 
files together, if any 
```
