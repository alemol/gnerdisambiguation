;Rules definition

;Fact descriptions:
; (in_db ?entity <yes|no>) : Determines the membership of ?entity in the gazetteer  
; (stack is_empty <yes|no>) : Indicates the state (empty, non-empty) of the desambiguation stack
; (predecessor ?A ?B <yes|no>): Relationship relative to the feature_code. A < B if the A.feature_code < B.feature_code 
; (association_between ?A ?B <yes|no>): Relationship relative to the feature_code. A < B if the A.feature_code< B.feature_code 

;Comments:
;When an entity E is added to the desambiguation stack there is the following regards:

; 1. If there are many instances of E with different features_codes, the instance of E with the highest feature is added to the desambiguation stack. 
; 2. If E is not in Gazzetteer, the value NULL is assigned to the feature_code of E. NULL is the lowest possible value of a feature_code. 

;About geolocation process.
; 3. The geolocation is carried out when there is not location entities to be processed.
; 4. The geolocation is based on  the desambiguation stack.
; 5. The geolocation process involves the following considerations

(defrule rule_00 "Empty --> NE in gazetteer"
	(in_db ?entity yes)
	(stack is_empty yes)	
=>
	(addLocation ?entity)
	(retract *)
)

(defrule rule_01 "NE in gazetteer --> NE with association top"
	(in_db ?entity yes)
	(predecessor ?entity ?top yes)
	(association_between ?entity ?top yes)
	(stack is_empty no)
=>
	(addLocationWithAssociation ?entity)
    (retract *)
)

(defrule rule_02 "NE in gazetteer --> NE without association top"
	(in_db ?entity yes)
	(predecessor ?entity ?top yes)
	(association_between ?entity ?top no)
	(stack is_empty no)
=>
	(addLocationWithoutAssociation ?entity)
    (retract *)
)

(defrule rule_03 "NE in gazetteer --> exchange with top"
	(in_db ?entity yes)
	(predecessor ?entity ?top no)
	(association_between ?entity ?top yes)
	(stack is_empty no)
=>
	(stackExchange ?entity)
	(retract *)
)

(defrule rule_04 "NE in gazetteer --> NE no in gazetteer"
	(in_db ?entity no)
	(stack is_empty no)
=>
    (associateConflictTop ?entity)
    (retract *)
)

(defrule rule_05 "Empty --> NE no in gazetteer"
	(in_db ?entity no)
	(stack is_empty yes)
=>
	(addConflictsStack ?entity)
	(retract *)
)

(defrule rule_06 "NE in gazetteer --> NE with association"
	(in_db ?entity yes)
	(predecessor ?entity ?top no)
	(association_between ?entity ?top no)
	(stack is_empty no)
=>
	(addLocation ?entity)
    (retract *)		
)

(defrule rule_07 "conflicts_stack --> stack"
	(more_locations no)
	(conflicts_stack is_empty no)
=>
	(conflictAddStack)
	(retract *)
)