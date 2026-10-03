// Idempotent by unique external ID. Trigger derives all decision outputs.
List<Recovery_Asset__c> assets = new List<Recovery_Asset__c>{
    new Recovery_Asset__c(External_Id__c='DEMO-001',Model__c='Atlas 14',Supplier__c='Northstar IT',Condition_Score__c=85,Resale_Price__c=1000,Refurbished_Price__c=1400,Repair_Cost__c=200,Failure_Probability__c=0.1,Salvage_Value__c=100,Acquisition_Credit__c=400,Logistics_Cost__c=50),
    new Recovery_Asset__c(External_Id__c='DEMO-002',Model__c='Orion 15',Supplier__c='Harbor Devices',Condition_Score__c=65,Resale_Price__c=900,Refurbished_Price__c=1400,Repair_Cost__c=850,Failure_Probability__c=0.55,Salvage_Value__c=150,Acquisition_Credit__c=600,Logistics_Cost__c=70),
    new Recovery_Asset__c(External_Id__c='DEMO-003',Model__c='Lumen 13',Supplier__c='Northstar IT',Condition_Score__c=20,Resale_Price__c=700,Refurbished_Price__c=1100,Repair_Cost__c=250,Failure_Probability__c=0.3,Salvage_Value__c=120,Acquisition_Credit__c=40,Logistics_Cost__c=30)
};
upsert assets External_Id__c;
System.debug('Seeded '+assets.size()+' synthetic recovery assets.');
