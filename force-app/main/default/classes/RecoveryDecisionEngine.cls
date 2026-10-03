public with sharing class RecoveryDecisionEngine {
    public static final String POLICY_VERSION = 'circular-v1';
    public class Decision {
        public String route;
        public Decimal expectedNet;
        public Decimal resaleNet;
        public Decimal repairNet;
        public Decimal recycleNet;
        public Boolean needsReview;
        public String reason;
    }
    public class InvalidInputException extends Exception {}
    public static Decision evaluate(Recovery_Asset__c a) {
        List<Decimal> amounts = new List<Decimal>{a.Resale_Price__c, a.Refurbished_Price__c,
            a.Repair_Cost__c, a.Salvage_Value__c, a.Acquisition_Credit__c, a.Logistics_Cost__c};
        for (Decimal amount : amounts) {
            if (amount == null || amount < 0) throw new InvalidInputException('All financial inputs must be nonnegative.');
        }
        if (a.Condition_Score__c == null || a.Condition_Score__c < 0 || a.Condition_Score__c > 100 ||
            a.Condition_Score__c != a.Condition_Score__c.setScale(0) ||
            a.Failure_Probability__c == null || a.Failure_Probability__c < 0 || a.Failure_Probability__c > 1) {
            throw new InvalidInputException('Condition must be an integer from 0 to 100; failure probability must be from 0 to 1.');
        }
        Decimal base = a.Acquisition_Credit__c + a.Logistics_Cost__c;
        Decision d = new Decision();
        d.resaleNet = a.Resale_Price__c - base;
        d.repairNet = (1-a.Failure_Probability__c)*a.Refurbished_Price__c +
            a.Failure_Probability__c*a.Salvage_Value__c - a.Repair_Cost__c - base;
        d.recycleNet = a.Salvage_Value__c - base;
        // Start with the most preferred eligible route. Compare unrounded values.
        if (a.Condition_Score__c >= 70) { d.route = 'Resale'; d.expectedNet = d.resaleNet; }
        else if (a.Condition_Score__c >= 30) { d.route = 'Repair'; d.expectedNet = d.repairNet; }
        else { d.route = 'Recycle'; d.expectedNet = d.recycleNet; }
        if (a.Condition_Score__c >= 30 && d.repairNet > d.expectedNet) { d.route = 'Repair'; d.expectedNet = d.repairNet; }
        if (d.recycleNet > d.expectedNet) { d.route = 'Recycle'; d.expectedNet = d.recycleNet; }
        d.needsReview = d.expectedNet < 0;
        d.reason = 'Best eligible expected net after credit, logistics and repair risk. ' +
            (d.needsReview ? 'Negative contribution: manager review required.' : 'Nonnegative expected contribution.');
        d.expectedNet = d.expectedNet.setScale(2, RoundingMode.HALF_UP);
        d.resaleNet = d.resaleNet.setScale(2, RoundingMode.HALF_UP);
        d.repairNet = d.repairNet.setScale(2, RoundingMode.HALF_UP);
        d.recycleNet = d.recycleNet.setScale(2, RoundingMode.HALF_UP);
        return d;
    }
    public static void apply(Recovery_Asset__c a, Decision d) {
        a.Route__c=d.route; a.Expected_Net__c=d.expectedNet; a.Resale_Net__c=d.resaleNet;
        a.Repair_Net__c=d.repairNet; a.Recycle_Net__c=d.recycleNet; a.Needs_Review__c=d.needsReview;
        a.Policy_Version__c=POLICY_VERSION; a.Decision_Reason__c=d.reason;
    }
}
