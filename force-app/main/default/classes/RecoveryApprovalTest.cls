@IsTest
private class RecoveryApprovalTest {
    @TestSetup static void usersAndPermissions() {
        Id profileId = [SELECT Id FROM Profile WHERE Name IN ('Standard User','Usuário Padrão') LIMIT 1].Id;
        Map<String,Id> sets = new Map<String,Id>();
        for(PermissionSet p : [SELECT Id,Name FROM PermissionSet WHERE Name IN
            ('Recovery_Operator','Recovery_Approver','Recovery_Manager')]) sets.put(p.Name,p.Id);
        List<User> users = new List<User>();
        for(String role : new List<String>{'Operator','Approver','Manager'}) {
            users.add(new User(FirstName='Portfolio',LastName='ReuseTest'+role,
                Alias='ru'+role.left(5),Email='reuse.'+role.toLowerCase()+'@example.invalid',
                Username='reuse.'+role.toLowerCase()+'.'+UserInfo.getOrganizationId()+'.'+
                    String.valueOf(Datetime.now().getTime())+'@example.invalid',
                ProfileId=profileId,TimeZoneSidKey='America/Sao_Paulo',LocaleSidKey='en_US',
                EmailEncodingKey='UTF-8',LanguageLocaleKey='en_US'));
        }
        insert users;
        List<PermissionSetAssignment> assignments = new List<PermissionSetAssignment>();
        for(User u : users) {
            assignments.add(new PermissionSetAssignment(AssigneeId=u.Id,PermissionSetId=sets.get('Recovery_Operator')));
            if(u.LastName=='ReuseTestApprover') assignments.add(new PermissionSetAssignment(AssigneeId=u.Id,PermissionSetId=sets.get('Recovery_Approver')));
            if(u.LastName=='ReuseTestManager') assignments.add(new PermissionSetAssignment(AssigneeId=u.Id,PermissionSetId=sets.get('Recovery_Manager')));
        }
        insert assignments;
    }
    private static User roleUser(String role) {
        String lastName='ReuseTest'+role;
        return [SELECT Id FROM User WHERE LastName=:lastName LIMIT 1];
    }
    private static Recovery_Asset__c evaluated(Decimal credit,Decimal condition) {
        Recovery_Asset__c a = new Recovery_Asset__c(External_Id__c='PERMISSION-'+credit+'-'+condition,
            Model__c='Atlas 14',Supplier__c='Demo Supplier',Condition_Score__c=condition,
            Resale_Price__c=1000,Refurbished_Price__c=1400,Repair_Cost__c=200,
            Failure_Probability__c=0.1,Salvage_Value__c=100,Acquisition_Credit__c=credit,Logistics_Cost__c=50);
        insert as user a;
        Recovery_Asset__c statusOnly = new Recovery_Asset__c(Id=a.Id,Status__c='Evaluated');
        update as user statusOnly;
        return a;
    }
    @IsTest static void operatorCannotApprove() {
        System.runAs(roleUser('Operator')) {
            Recovery_Asset__c a=evaluated(400,85);
            Database.SaveResult r=Database.update(new Recovery_Asset__c(Id=a.Id,Status__c='Approved'),false,AccessLevel.USER_MODE);
            System.assertEquals(false,r.isSuccess());
        }
    }
    @IsTest static void approverCanApproveOrdinaryCase() {
        System.runAs(roleUser('Approver')) {
            Recovery_Asset__c a=evaluated(400,85); RecoveryController.approveAsset(a.Id);
            System.assertEquals('Approved',[SELECT Status__c FROM Recovery_Asset__c WHERE Id=:a.Id].Status__c);
        }
    }
    @IsTest static void approverCannotApproveExceptions() {
        System.runAs(roleUser('Approver')) {
            Recovery_Asset__c highCredit=evaluated(600,85);
            Recovery_Asset__c negative=evaluated(400,20);
            for(Recovery_Asset__c a : new List<Recovery_Asset__c>{highCredit,negative}) {
                Database.SaveResult r=Database.update(new Recovery_Asset__c(Id=a.Id,Status__c='Approved'),false,AccessLevel.USER_MODE);
                System.assertEquals(false,r.isSuccess());
            }
        }
    }
    @IsTest static void managerApprovalAndInvalidation() {
        System.runAs(roleUser('Manager')) {
            Recovery_Asset__c a=evaluated(600,85); RecoveryController.approveAsset(a.Id);
            System.assertEquals('Approved',[SELECT Status__c FROM Recovery_Asset__c WHERE Id=:a.Id].Status__c);
            update as user new Recovery_Asset__c(Id=a.Id,Repair_Cost__c=900);
            System.assertEquals('Draft',[SELECT Status__c FROM Recovery_Asset__c WHERE Id=:a.Id].Status__c);
        }
    }
    @IsTest static void privateSharingHidesOtherOwnersRecords() {
        Id assetId;
        System.runAs(roleUser('Operator')) { assetId=evaluated(400,85).Id; }
        System.runAs(roleUser('Approver')) {
            Boolean rejected=false;
            try { RecoveryController.evaluateAssets(new List<Id>{assetId}); }
            catch(AuraHandledException e) { rejected=true; }
            System.assertEquals(true,rejected);
        }
    }
}
