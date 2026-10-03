public with sharing class RecoveryAssetHandler {
    private static final List<String> INPUTS = new List<String>{'External_Id__c','Condition_Score__c', 'Resale_Price__c',
        'Refurbished_Price__c','Repair_Cost__c','Failure_Probability__c','Salvage_Value__c',
        'Acquisition_Credit__c','Logistics_Cost__c','Model__c','Supplier__c'};
    public static void beforeSave(List<Recovery_Asset__c> assets, Map<Id,Recovery_Asset__c> oldMap) {
        for (Recovery_Asset__c a : assets) {
            if (String.isBlank(a.External_Id__c) || String.isBlank(a.Model__c) || String.isBlank(a.Supplier__c)) {
                a.addError('External ID, model and supplier are required.'); continue;
            }
            Recovery_Asset__c old = oldMap == null ? null : oldMap.get(a.Id);
            Boolean changed = old == null;
            if (old != null) for (String field : INPUTS) { if (a.get(field) != old.get(field)) changed = true; }
            if (a.Status__c == 'Approved' && (old == null || old.Status__c != 'Approved')) {
                if (old == null || old.Status__c != 'Evaluated' || changed) {
                    a.addError('Evaluate unchanged inputs before approval.'); continue;
                }
                if (!FeatureManagement.checkPermission('Recovery_Approve')) {
                    a.addError('Recovery approval permission is required.'); continue;
                }
                if ((a.Acquisition_Credit__c > 500 || old.Needs_Review__c) &&
                    !FeatureManagement.checkPermission('Recovery_Manager')) {
                    a.addError('Manager approval is required for credit above 500 or negative contribution.'); continue;
                }
            }
            if (changed) a.Status__c = 'Draft';
            try { RecoveryDecisionEngine.apply(a, RecoveryDecisionEngine.evaluate(a)); }
            catch (RecoveryDecisionEngine.InvalidInputException e) { a.addError(e.getMessage()); }
        }
    }
}
