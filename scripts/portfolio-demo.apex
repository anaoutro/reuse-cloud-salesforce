// Evaluate only explicitly synthetic portfolio assets.
Set<Id> ids=new Set<Id>();for(Recovery_Asset__c a:[SELECT Id FROM Recovery_Asset__c WHERE External_Id__c LIKE 'DEMO-%'])ids.add(a.Id);
if(!ids.isEmpty())System.enqueueJob(new RecoveryEvaluationJob(ids));
