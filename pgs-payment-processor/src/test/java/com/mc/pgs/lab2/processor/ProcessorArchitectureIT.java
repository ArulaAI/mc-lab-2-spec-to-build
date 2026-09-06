package com.mc.pgs.lab2.processor;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

/**
 * Structural rules that fail the build rather than a review.
 *
 * <p>Two deliberate choices here, both learned the hard way:
 * <ul>
 *   <li>Tests are excluded. These rules describe the shape of the production code; a test that
 *       reaches across layers to set up a fixture is not an architecture violation.</li>
 *   <li>Package patterns are anchored to {@code com.mc.pgs.lab2.processor}, not written as
 *       {@code ..api..}. An unanchored {@code ..api..} also matches third-party packages such as
 *       {@code org.assertj.core.api}, which produces confident, entirely bogus violations.</li>
 * </ul>
 */
@AnalyzeClasses(
        packages = "com.mc.pgs.lab2.processor",
        importOptions = ImportOption.DoNotIncludeTests.class)
class ProcessorArchitectureIT {

    private static final String API = "com.mc.pgs.lab2.processor.api..";
    private static final String CLIENT = "com.mc.pgs.lab2.processor.client..";
    private static final String CONFIG = "com.mc.pgs.lab2.processor.config..";
    private static final String DOMAIN = "com.mc.pgs.lab2.processor.domain..";
    private static final String REPO = "com.mc.pgs.lab2.processor.repo..";

    @ArchTest
    static final ArchRule controllersDoNotReachPastTheServiceLayer =
            noClasses().that().resideInAPackage(API)
                    .should().dependOnClassesThat().resideInAPackage(REPO)
                    .because("controllers hold HTTP concerns only; persistence is reached through the service layer");

    @ArchTest
    static final ArchRule domainStaysFreeOfInfrastructure =
            noClasses().that().resideInAPackage(DOMAIN)
                    .should().dependOnClassesThat().resideInAnyPackage(API, CLIENT, CONFIG, REPO)
                    .because("the domain model is the root of business logic and carries no infrastructure concerns");

    @ArchTest
    static final ArchRule noSettlementArtifactIsEverProduced =
            noClasses().that().resideInAPackage("com.mc.pgs.lab2.processor..")
                    .should().haveSimpleNameContaining("Settlement")
                    .because("settlement, injection, LCS and DCF are downstream and outside this service");
}
