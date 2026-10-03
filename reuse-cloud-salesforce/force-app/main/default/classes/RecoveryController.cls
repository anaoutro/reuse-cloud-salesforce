public with sharing class RecoveryController {
    @AuraEnabled(cacheable=true)
    public static List<Recovery_Asset__c> getAssets() {
        return [SELECT Id, Name, External_Id__c, Model__c, Supplier__c, Condition_Score__c,
            Route__c, Expected_Net__c, Resale_Net__c, Repair_Net__c, Recycle_Net__c,
            Needs_Review__c, Status__c, Acquisition_Credit__c, Policy_Version__c, Decision_Reason__c
            FROM Recovery_Asset__c WITH USER_MODE ORDER BY CreatedDate DESC LIMIT 200];
    }
    @AuraEnabled
    public static Id evaluateAssets(List<Id> ids) {
        if (ids == null || ids.isEmpty() || ids.size() > 200) throw new AuraHandledException('Select 1 to 200 assets.');
        Set<Id> requested = new Set<Id>(ids);
        List<Recovery_Asset__c> visible = [SELECT Id FROM Recovery_Asset__c WHERE Id IN :requested WITH USER_MODE];
        if (visible.size() != requested.size()) throw new AuraHandledException('Some assets are unavailable.');
        return System.enqueueJob(new RecoveryEvaluationJob(requested));
    }
    @AuraEnabled
    public static void approveAsset(Id assetId) {
        if (assetId == null) throw new AuraHandledException('Select an asset.');
        Recovery_Asset__c a = [SELECT Id, Status__c FROM Recovery_Asset__c WHERE Id=:assetId WITH USER_MODE FOR UPDATE];
        if (a.Status__c != 'Evaluated') throw new AuraHandledException('Evaluate this asset before approval.');
        a.Status__c='Approved';
        update as user a;
    }
}
