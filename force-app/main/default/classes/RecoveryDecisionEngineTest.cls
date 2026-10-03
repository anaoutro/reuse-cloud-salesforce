@IsTest
private class RecoveryDecisionEngineTest {
    static Recovery_Asset__c asset(String key, Decimal condition) {
        return new Recovery_Asset__c(External_Id__c=key,Model__c='Atlas 14',Supplier__c='Demo Supplier',
            Condition_Score__c=condition,Resale_Price__c=1000,Refurbished_Price__c=1400,
            Repair_Cost__c=200,Failure_Probability__c=0.1,Salvage_Value__c=100,
            Acquisition_Credit__c=400,Logistics_Cost__c=50);
    }
    @IsTest static void repairRiskAndCondition() {
        RecoveryDecisionEngine.Decision d=RecoveryDecisionEngine.evaluate(asset('A',80));
        System.assertEquals('Repair',d.route); System.assertEquals(620,d.expectedNet);
        d=RecoveryDecisionEngine.evaluate(asset('B',20));
        System.assertEquals('Recycle',d.route); System.assertEquals(-350,d.expectedNet);
        System.assertEquals(true,d.needsReview);
    }
    @IsTest static void tiePrefersResale() {
        Recovery_Asset__c a=asset('C',70); a.Refurbished_Price__c=1000;
        a.Failure_Probability__c=0; a.Repair_Cost__c=0;
        System.assertEquals('Resale',RecoveryDecisionEngine.evaluate(a).route);
    }
    @IsTest static void boundariesAndRounding() {
        System.assertEquals('Repair',RecoveryDecisionEngine.evaluate(asset('D',30)).route);
        System.assertEquals('Recycle',RecoveryDecisionEngine.evaluate(asset('E',29)).route);
        Recovery_Asset__c a=asset('F',80); a.Failure_Probability__c=1;
        System.assertEquals('Resale',RecoveryDecisionEngine.evaluate(a).route);
        a.Resale_Price__c=1000.005;
        System.assertEquals(550.01,RecoveryDecisionEngine.evaluate(a).expectedNet);
    }
    @IsTest static void rejectsInvalidInputs() {
        Recovery_Asset__c a=asset('G',80); a.Failure_Probability__c=1.1;
        Boolean rejected=false;
        try { RecoveryDecisionEngine.evaluate(a); } catch(RecoveryDecisionEngine.InvalidInputException e) { rejected=true; }
        System.assertEquals(true,rejected);
    }
    @IsTest static void bulkAndInvalidation() {
        List<Recovery_Asset__c> assets=new List<Recovery_Asset__c>();
        for(Integer i=0;i<200;i++) assets.add(asset('BULK-'+i,80));
        insert assets;
        Set<Id> ids=new Map<Id,Recovery_Asset__c>(assets).keySet();
        Test.startTest(); System.enqueueJob(new RecoveryEvaluationJob(ids)); Test.stopTest();
        System.assertEquals(200,[SELECT count() FROM Recovery_Asset__c WHERE Status__c='Evaluated']);
        Recovery_Asset__c first=[SELECT Id, Repair_Cost__c FROM Recovery_Asset__c LIMIT 1];
        first.Repair_Cost__c=900; update first;
        first=[SELECT Status__c, Route__c FROM Recovery_Asset__c WHERE Id=:first.Id];
        System.assertEquals('Draft',first.Status__c); System.assertEquals('Resale',first.Route__c);
    }
    @IsTest static void duplicateExternalId() {
        insert asset('SAME',80);
        Database.SaveResult result=Database.insert(asset('SAME',80),false);
        System.assertEquals(false,result.isSuccess());
    }
    @IsTest static void identityChangeInvalidatesEvaluation() {
        Recovery_Asset__c a=asset('IDENTITY-A',80); insert a;
        a.Status__c='Evaluated'; update a;
        a.External_Id__c='IDENTITY-B'; update a;
        System.assertEquals('Draft',[SELECT Status__c FROM Recovery_Asset__c WHERE Id=:a.Id].Status__c);
    }
    @IsTest static void protectsDerivedFields() {
        Recovery_Asset__c a=asset('DERIVED',80); insert a;
        a.Expected_Net__c=999999; update a;
        System.assertEquals(620,[SELECT Expected_Net__c FROM Recovery_Asset__c WHERE Id=:a.Id].Expected_Net__c);
    }
    @IsTest static void approvalNeedsEvaluation() {
        Recovery_Asset__c a=asset('APPROVE',80); insert a;
        a.Status__c='Approved'; Database.SaveResult result=Database.update(a,false);
        System.assertEquals(false,result.isSuccess());
    }
    @IsTest static void repeatJobSkipsEvaluatedState() {
        Recovery_Asset__c a=asset('REPEAT',80); insert a;
        a.Status__c='Evaluated'; update a;
        Test.startTest(); RecoveryController.evaluateAssets(new List<Id>{a.Id}); Test.stopTest();
        System.assertEquals('Evaluated',[SELECT Status__c FROM Recovery_Asset__c WHERE Id=:a.Id].Status__c);
    }
}
