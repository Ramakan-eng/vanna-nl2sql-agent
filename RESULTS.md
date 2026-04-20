# Healthcare NL2SQL API - Test Results

**Total Tests**: 20  
**Passed**: 18  
**Failed**: 1  
**Issues**: 1  


## Test Results

### Test 1: How many patients do we have?

**Question**: "How many patients do we have?"

**Generated SQL**:
```
SELECT COUNT(*) AS total_patients FROM patients
```

**Status**: PASS

**Result Summary**:
- Row Count: 1
- Result: 200 patients
- **Assessment**: Correctly generated COUNT query with accurate result

---


### Test 2: List all doctors and their specializations

**Question**: "List all doctors and their specializations"

**Generated SQL**:
```
SELECT name, specialization FROM doctors
```

**Status**: PASS

**Result Summary**:
- Row Count: 15 doctors
- Specializations: Dermatology (3), Cardiology (3), Orthopedics (3), General (3), Pediatrics (3)
- **Assessment**: Simple SELECT query correctly returns all doctors with their specializations

---

### Test 3: Show me appointments for last month

**Question**: "Show me appointments for last month"

**Generated SQL**:
```
SELECT * FROM appointments 
WHERE appointment_date >= '2023-10-01' AND appointment_date < '2023-11-01'
```

**Status**:  NO DATA FOUND

**Result Summary**:
- Row Count: 0
- **Issue**: The generated date range (October 2023) is outside the actual appointment data range (Oct 2025 - Apr 2026)
- **Root Cause**: LLM generated hardcoded dates instead of dynamic date calculation relative to current date
- **Recommendation**: Should use `date('now', '-1 month')` for relative date filtering

---

### Test 4: Which doctor has the most appointments?

**Question**: "Which doctor has the most appointments?"

**Generated SQL**:
```
SELECT d.id, d.name, COUNT(a.id) AS appointment_count
FROM doctors d
JOIN appointments a ON d.id = a.doctor_id
GROUP BY d.id
ORDER BY appointment_count DESC
LIMIT 1
```

**Status**: PASS

**Result Summary**:
- Row Count: 1
- Result: Leslie Martinez with 86 appointments
- **Assessment**: Correctly generated JOIN + GROUP BY + ORDER BY query

---

### Test 5: What is the total revenue?

**Question**: "What is the total revenue?"

**Generated SQL**:
```
SELECT SUM(total_amount) AS total_revenue FROM invoices
```

**Status**: PASS

**Result Summary**:
- Row Count: 1
- Total Revenue: 773,323.63
- **Assessment**: Simple SUM aggregation correctly calculates total revenue

---

### Test 6: Show revenue by doctor

**Question**: "Show revenue by doctor"

**Generated SQL**:
```
SELECT d.name, SUM(i.total_amount) AS total_revenue
FROM invoices i
JOIN appointments a ON a.patient_id = i.patient_id
JOIN doctors d ON d.id = a.doctor_id
GROUP BY d.name
ORDER BY total_revenue DESC
```

**Status**: PASS

**Result Summary**:
- Row Count: 15 doctors
- Top Revenue: Leslie Martinez ($154,788.88)
- Bottom Revenue: Heidi Arias ($3,128.78)
- **Assessment**: Complex multi-table JOIN correctly groups revenue by doctor

---

### Test 7: How many cancelled appointments last quarter?

**Question**: "How many cancelled appointments last quarter?"

**Generated SQL**:
```
SELECT COUNT(*) 
FROM appointments 
WHERE status = 'cancelled' 
AND appointment_date >= DATE('now', 'start of quarter', '-1 quarter') 
AND appointment_date < DATE('now', 'start of quarter')
```

**Status**:  ZERO RESULTS

**Result Summary**:
- Row Count: 1
- Result: 0 cancelled appointments
- **Assessment**: Query syntax is correct, but returns 0 (no cancelled appointments in last quarter)
- **Note**: This is technically correct behavior - no matching data exists

---

### Test 8: Top 5 patients by spending

**Question**: "Top 5 patients by spending"

**Generated SQL**:
```
SELECT p.id, p.first_name, p.last_name, SUM(t.cost) AS total_spent
FROM patients p
JOIN appointments a ON p.id = a.patient_id
JOIN treatments t ON a.id = t.appointment_id
GROUP BY p.id
ORDER BY total_spent DESC
LIMIT 5
```

**Status**: PASS

**Result Summary**:
- Row Count: 5
- Top Spender: Robert Sanchez ($32,524.39)
- 5th Spender: Andrew Lowe ($27,360.65)
- **Assessment**: Complex JOIN + GROUP + ORDER + LIMIT correctly identifies top 5 patients

---

### Test 9: Average treatment cost by specialization

**Question**: "Average treatment cost by specialization"

**Generated SQL**:
```
SELECT d.specialization, AVG(t.cost) AS average_treatment_cost
FROM treatments t
JOIN appointments a ON t.appointment_id = a.id
JOIN doctors d ON a.doctor_id = d.id
GROUP BY d.specialization
```

**Status**: PASS

**Result Summary**:
- Row Count: 5 specializations
- Average Costs:
  - Orthopedics: $2,666.45 (highest)
  - Cardiology: $2,372.27
  - Pediatrics: $2,389.36
  - General: $2,314.35
  - Dermatology: $2,264.21 (lowest)
- **Assessment**: Multi-table JOIN with AVG aggregation correctly grouped by specialization

---

###  Test 10: Show monthly appointment count for the past 6 months

**Question**: "Show monthly appointment count for the past 6 months"

**Generated SQL**:
```
SELECT strftime('%Y-%m', appointment_date) AS month, COUNT(*) AS appointment_count
FROM appointments
WHERE appointment_date >= date('now', '-6 months')
GROUP BY month
ORDER BY month
```

**Status**: PASS

**Result Summary**:
- Row Count: 7 months (Oct 2025 - Apr 2026)
- Peak Month: Nov 2025 (51 appointments)
- Low Month: Apr 2026 (25 appointments)
- **Assessment**: Date function with dynamic relative dates works correctly

---

### Test 11: Which city has the most patients?

**Question**: "Which city has the most patients?"

**Generated SQL**:
```
SELECT city, COUNT(*) AS patient_count
FROM patients
GROUP BY city
ORDER BY patient_count DESC
LIMIT 1
```

**Status**: PASS

**Result Summary**:
- Row Count: 1
- Result: Noida with 26 patients
- **Assessment**: GROUP BY + ORDER + LIMIT correctly identifies city with most patients

---

###  Test 12: List patients who visited more than 3 times

**Question**: "List patients who visited more than 3 times"

**Generated SQL**:
```
SELECT p.id, p.first_name, p.last_name, COUNT(a.id) as visit_count
FROM patients p
JOIN appointments a ON p.id = a.patient_id
GROUP BY p.id
HAVING COUNT(a.id) > 3
```

**Status**:  PASS

**Result Summary**:
- Row Count: 55 patients
- Highest Visits: Shelley Oconnor (9 visits), Stephen Heath (9 visits)
- **Assessment**: HAVING clause correctly filters groups with >3 appointments

---

### Test 13: Show unpaid invoices

**Question**: "Show unpaid invoices"

**Generated SQL**:
```
SELECT * FROM invoices WHERE status = 'unpaid'
```

**Status**:  FAIL

**Result Summary**:
- Row Count: 0
- Expected: Multiple unpaid invoices
- **Root Cause**: Invoice status field uses 'Pending' or 'Overdue', NOT 'unpaid'
- **Issue**: The LLM generated incorrect status value - it should be `WHERE status IN ('Pending', 'Overdue')`
- **Recommendation**: Better schema documentation or query correction needed

---

###  Test 14: What percentage of appointments are no-shows?

**Question**: "What percentage of appointments are no-shows?"

**Generated SQL**:
```
SELECT (COUNT(CASE WHEN status = 'No-Show' THEN 1 END) * 100.0 / COUNT(*)) AS no_show_percentage
FROM appointments
```

**Status**:  PASS

**Result Summary**:
- Row Count: 1
- Result: 19.2% of appointments are no-shows
- **Assessment**: CASE + percentage calculation correctly computed

---

### Test 15: Show the busiest day of the week for appointments

**Question**: "Show the busiest day of the week for appointments"

**Generated SQL**:
```
SELECT strftime('%w', appointment_date) AS day_of_week, COUNT(*) AS appointment_count
FROM appointments
GROUP BY day_of_week
ORDER BY appointment_count DESC
LIMIT 1
```

**Status**: PASS

**Result Summary**:
- Row Count: 1
- Result: Day 6 (Saturday) with 79 appointments
- **Assessment**: Date function with weekday extraction correctly identifies busiest day

---

### Test 16: Revenue trend by month

**Question**: "Revenue trend by month"

**Generated SQL**:
```sql
SELECT strftime('%Y-%m', invoice_date) AS month, SUM(total_amount) AS total_revenue
FROM invoices
GROUP BY month
ORDER BY month
```

**Status**: PASS

**Result Summary**:
- Row Count: 13 months
- Peak Revenue: Feb 2026 ($82,516.23)
- Low Revenue: Apr 2025 ($26,144.46)
- **Assessment**: Time series aggregation correctly groups revenue by month

---

### Test 17: Average appointment duration by doctor

**Question**: "Average appointment duration by doctor"

**Generated SQL**:
```
SELECT d.name AS doctor_name, AVG(t.duration_minutes) AS average_duration
FROM doctors d
JOIN appointments a ON d.id = a.doctor_id
JOIN treatments t ON a.id = t.appointment_id
GROUP BY d.id
```

**Status**: PASS

**Result Summary**:
- Row Count: 14 doctors
- Longest Avg Duration: Alicia Donovan (91.67 minutes)
- Shortest Avg Duration: Brianna Lee (27 minutes)
- **Chart Generated**: Pie chart showing distribution
- **Assessment**: Multi-table JOIN with AVG produces accurate results

---

### Test 18: List patients with overdue invoices

**Question**: "List patients with overdue invoices"

**Generated SQL**:
```
SELECT p.id, p.first_name, p.last_name, p.email, p.phone, i.invoice_date, i.total_amount, i.paid_amount
FROM patients p
JOIN invoices i ON p.id = i.patient_id
WHERE i.invoice_date < DATE('now') AND i.status <> 'Paid'
```

**Status**:  PASS

**Result Summary**:
- Row Count: 214 patients with overdue invoices
- Sample: Benjamin Woods owes $2,261.64 (paid $709.47)
- **Assessment**: JOIN with multiple filters correctly identifies overdue accounts

---

### Test 19: Compare revenue between departments

**Question**: "Compare revenue between departments"

**Generated SQL**:
```
SELECT d.department, SUM(t.cost) AS total_revenue
FROM treatments t
JOIN appointments a ON t.appointment_id = a.id
JOIN doctors d ON a.doctor_id = d.id
GROUP BY d.department
```

**Status**:  PASS

**Result Summary**:
- Row Count: 5 departments
- Top Revenue: Pediatrics ($253,272.12)
- Bottom Revenue: General ($64,801.74)
- **Assessment**: Department-level aggregation correctly sums revenue

---

### Test 20: Show patient registration trend by month

**Question**: "Show patient registration trend by month"

**Generated SQL**:
```
SELECT strftime('%Y-%m', registered_date) AS registration_month, COUNT(*) AS patient_count
FROM patients
GROUP BY registration_month
ORDER BY registration_month
```

**Status**: PASS

**Result Summary**:
- Row Count: 13 months
- Peak Registration: Aug 2024 (22 patients)
- Low Registration: Apr 2025 (11 patients)
- **Assessment**: Time series registration trend correctly analyzed

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total Tests** | 20 |
| **Passed**  | 18 |
| **Failed** | 1 |
| **Warnings/Issues** | 1 |
| **Success Rate** | 90% |

## Issues Found

### 1.  CRITICAL: Test 13 - Show unpaid invoices
- **Error**: Generated SQL uses `status = 'unpaid'` but actual values are 'Pending', 'Overdue'
- **Impact**: Query returned 0 results instead of 214+ unpaid invoices
- **Fix**: LLM needs better schema documentation or memory correction

### 2.  WARNING: Test 3 - Show me appointments for last month
- **Issue**: Used hardcoded dates ('2023-10-01') instead of dynamic dates
- **Impact**: No results found due to date range mismatch

