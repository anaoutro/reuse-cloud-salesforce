public with sharing class RecoveryEvaluationJob implements Queueable {
    private Set<Id> assetIds;
    public RecoveryEvaluationJob(Set<Id> ids) { assetIds = ids; }
    public void execute(QueueableContext context) {
        // Re-query current inputs. Lock rows so concurrent jobs cannot overwrite approval.
        List<Recovery_Asset__c> assets = [SELECT Id, Status__c FROM Recovery_Asset__c
            WHERE Id IN :assetIds WITH USER_MODE FOR UPDATE];
        List<Recovery_Asset__c> updates = new List<Recovery_Asset__c>();
        for (Recovery_Asset__c a : assets) {
            if (a.Status__c == 'Draft') updates.add(new Recovery_Asset__c(Id=a.Id,Status__c='Evaluated'));
        }
        if (!updates.isEmpty()) update as user updates;
        // The trigger recomputes outputs from complete current records in Trigger.new.
        // Repeated jobs skip already evaluated or approved assets.
    }
}
