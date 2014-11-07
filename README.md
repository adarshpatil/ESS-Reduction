ESS-Reduction
=============

Aim
----

Database Systems - IISc Course Project
- We aim to enhance the performance of the [Plan Bouquet] algorithm for query processing,  proposed in the paper presented at VLDB 2014. The paper defines plan bouquet approach as:
> In this paper, we investigate a conceptually new approach, wherein
the compile-time estimation process is completely eschewed for
error-prone selectivities. Instead, these selectivities are systemat-
ically discovered at run-time through a calibrated sequence of cost-
limited executions of a set of bouquet plans.
- Firstly, this code above attempts to find the ESS dimension which on reduction would result in least performance reduction
- Secondly, it identifies the "best" bouquet of plans along with the budgets to be executed
- Further Details of this project are here in my blog: http://adarshpatil.in/timewarp/projects/error-prone-predicates.html

[Plan Bouquet]:http://dsl.serc.iisc.ernet.in/projects/QUEST/index.html#pub

License
----

MIT

**Free Software, Hell Yeah!**
