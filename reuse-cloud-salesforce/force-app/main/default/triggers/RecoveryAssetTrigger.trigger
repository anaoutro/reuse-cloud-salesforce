trigger RecoveryAssetTrigger on Recovery_Asset__c (before insert, before update) {
    RecoveryAssetHandler.beforeSave(Trigger.new, Trigger.isUpdate ? Trigger.oldMap : null);
}