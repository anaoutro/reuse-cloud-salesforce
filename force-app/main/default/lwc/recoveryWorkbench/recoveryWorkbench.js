import { LightningElement, wire } from 'lwc';
import getAssets from '@salesforce/apex/RecoveryController.getAssets';
import evaluateAssets from '@salesforce/apex/RecoveryController.evaluateAssets';
import approveAsset from '@salesforce/apex/RecoveryController.approveAsset';
import { refreshApex } from '@salesforce/apex';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

const columns = [
    { label: 'Asset', fieldName: 'External_Id__c' }, { label: 'Model', fieldName: 'Model__c' },
    { label: 'Condition', fieldName: 'Condition_Score__c', type: 'number' },
    { label: 'Route', fieldName: 'Route__c' },
    { label: 'Expected net', fieldName: 'Expected_Net__c', type: 'currency', typeAttributes: { currencyCode: 'BRL' } },
    { label: 'Review', fieldName: 'Needs_Review__c', type: 'boolean' },
    { label: 'Status', fieldName: 'Status__c' },
    { type: 'button', typeAttributes: { label: 'Inspect', name: 'inspect' } }
];
export default class RecoveryWorkbench extends LightningElement {
    columns = columns; assets = []; selected = []; inspected; result; busy = false;
    @wire(getAssets) wiredAssets(result) {
        this.result = result;
        if (result.data) { this.assets = result.data; if(this.inspected) this.inspected = this.assets.find(a => a.Id === this.inspected.Id); }
        if (result.error) this.notify('Unable to load assets', result.error.body?.message || result.error.message, 'error');
    }
    get loadedCount(){return this.assets.length;}
    get evaluatedCount(){return this.assets.filter(a=>a.Status__c==='Evaluated').length;}
    get approvedCount(){return this.assets.filter(a=>a.Status__c==='Approved').length;}
    get reviewCount(){return this.assets.filter(a=>a.Needs_Review__c).length;}
    get totalContribution(){return this.assets.reduce((n,a)=>n+Number(a.Expected_Net__c||0),0);}
    get noSelection() { return this.busy || !this.selected.length; }
    get cannotApprove() { return this.busy || !this.inspected || this.inspected.Status__c !== 'Evaluated'; }
    select(event) { this.selected = event.detail.selectedRows.map(a => a.Id); }
    inspect(event) { this.inspected = event.detail.row; }
    notify(title, message, variant) { this.dispatchEvent(new ShowToastEvent({title, message, variant})); }
    async evaluate() {
        this.busy = true;
        try { const job = await evaluateAssets({ ids: this.selected }); this.notify('Evaluation queued', 'Job ' + job + '. Click Refresh after the job completes.', 'success'); }
        catch (e) { this.notify('Evaluation failed', e.body?.message || e.message, 'error'); }
        finally { this.busy = false; }
    }
    async refresh() { this.busy=true; try { await refreshApex(this.result); } finally { this.busy=false; } }
    async approve() {
        this.busy=true;
        try { await approveAsset({assetId:this.inspected.Id}); await refreshApex(this.result); this.notify('Approved', 'Decision approved under circular-v1.', 'success'); }
        catch(e) { this.notify('Approval failed',e.body?.message || e.message,'error'); }
        finally { this.busy=false; }
    }
}