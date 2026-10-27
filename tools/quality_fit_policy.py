"""Transparent desktop ranking plus separate block rejection decisions."""
WEIGHTS={'block':.30,'physical_context':.10,'commute':.30,'acquisition':.20,'usable_inventory':.10}
ANCHORS={'UH':.25,'TSU':.15,'TMC':.30,'UHD':.15,'HCC Central':.10,'Rice':.05}

def clamp(x):return max(0,min(100,x))

def descending(value,best,worst):
    return clamp(100*(worst-value)/(worst-best)) if value is not None else 0

def desktop_score(pocket,eligible_count,market):
    b=pocket['block_quality'];n=b['n'];ctx=pocket['physical_context']
    block=clamp(100-10*b['median_serious_incidents_660ft']-2*b['p90_serious_incidents_660ft']-50*b['repeat_violence_review_sites']/n)
    physical=clamp(80*ctx['median_residential_share_660ft']+20*min(1,ctx['sites_new_res_permits_within_500ft']/n/.5)
        -25*ctx['sites_industrial_centroid_within_330ft']/n-25*ctx['sites_freeway_within_330ft']/n)
    distances=pocket['commute']['anchor_distance_miles_straight_line']
    minutes=pocket['commute']['scheduled_transit_median_minutes']
    geographic=sum(w*descending(distances[k],1,10) for k,w in ANCHORS.items())
    transit=sum(w*descending(minutes[k],20,90) for k,w in ANCHORS.items())
    commute=(geographic+transit)/2
    assessed=descending(pocket['median_assessed_land_psf'],8,30)
    negotiation=50*min(1,market['median_dom']/90)+50*min(1,market['price_drop_pct']/50)
    acquisition=(assessed+negotiation)/2
    inventory=100*min(1,eligible_count/60)
    components={'block':block,'physical_context':physical,'commute':commute,'acquisition':acquisition,'usable_inventory':inventory}
    return {'score':round(sum(components[k]*w for k,w in WEIGHTS.items())),
            'components':{k:round(v,1) for k,v in components.items()},
            'weights':WEIGHTS,'status':'desktop; field visit pending'}

def review_lane(site):
    field=site['block_quality'].get('field_rejection_reason')
    if field:return 'reject_for_buyer_tour'
    if site['minimum_lot_above_equal_half']:return 'resolve_minimum_lot_control'
    if site['sfha']:return 'resolve_flood_fit'
    if site['block_quality']['repeat_violence_review']:return 'inspect_repeat_violence_before_buyer_tour'
    return 'field_reconnaissance'
