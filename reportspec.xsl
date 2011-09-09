<xsl:transform
    version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:h="http://www.w3.org/1999/xhtml">

<xsl:output method="xml" indent="yes" />

<xsl:template match="h:html">
  <xsl:variable name="fs">
    <xsl:choose>
      <xsl:when test="contains(h:body/@class, 'medium-print')">9pt</xsl:when>
      <xsl:otherwise>10pt</xsl:otherwise> <!-- hmm... default size? -->
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="o">
    <xsl:choose>
      <xsl:when test="contains(h:body/@class, 'landscape')"
		>landscape</xsl:when>
      <xsl:otherwise>portrait</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <Report fontSize="{$fs}" orientation="{$o}">
    <xsl:apply-templates />
  </Report>
</xsl:template>

<xsl:template match="h:h1[contains(@class, 'ReportHeader')]">
  <ReportHeader>
    <Output>
      <!-- todo: trigger black/white on class="reversed" -->
      <Line fontSize="12" bgcolor="'black'" color="'white'">
	<literal width="2"/>
	<literal width="{string-length(text())}">
	  <xsl:value-of select="text()" />
	</literal>
      </Line>
    </Output>
  </ReportHeader>
</xsl:template>

<xsl:template match="h:h2[@class='PageHeader']">
  <PageHeader>
    <Output>
      <HorizontalLine size="4" bgcolor="'white'"/>
      <Line fontSize="11" bgcolor="'0xd0d0d0'" color="'black'">
	<literal width="2"/>
	<xsl:apply-templates mode="Line" />
      </Line>
      <HorizontalLine size="2" bgcolor="'white'" />
    </Output>
  </PageHeader>
</xsl:template>

<xsl:template match="*[contains(@class, 'literal')]" mode="Line">
  <!-- todo: alignment? -->
  <literal width="{string-length(text())}">
    <xsl:choose>
      <xsl:when test="contains(@class, 'blank')"
		></xsl:when>
      <xsl:otherwise
		><xsl:value-of select="text()"/></xsl:otherwise>
    </xsl:choose>
  </literal>
</xsl:template>

<xsl:template match="*[contains(@class, 'field')]" mode="Line">
  <field width="{string-length(text())}" value="{@title}"/>
</xsl:template>


<xsl:template match="h:table[@class='Detail']">
  <Detail>
    <xsl:apply-templates />
  </Detail>
</xsl:template>

<!-- todo: breaks -->
<xsl:template match="h:table[@class='Detail']/h:thead/h:tr[1]">
  <FieldHeaders>
    <Output>
      <HorizontalLine size="1" bgcolor="'black'"/>
      <Line bgcolor="'0xe5e5e5'" bold="true">
	<xsl:call-template name="line_th">
	  <xsl:with-param name="col" select="1" />
	</xsl:call-template>
      </Line>
      <HorizontalLine size="1" bgcolor="'black'"/>
      <HorizontalLine size="4" bgcolor="'white'"/>
    </Output>
  </FieldHeaders>
</xsl:template>

<xsl:template name="line_th">
  <xsl:param name="col" />
  <xsl:variable name="th_elt"
		select="h:th[position()=$col]" />

  <xsl:choose>
    <xsl:when test="$th_elt">
      <xsl:for-each select="$th_elt">
	<literal width="1"/>
	<xsl:variable name="width"
		      select="string-length(../../..
			      /h:tbody/h:tr[1]/h:td[$col]/text())"/>
	<literal width="{$width}" align="{@align}">
	  <xsl:value-of select="text()"/>
	</literal>
	
      </xsl:for-each>
      <xsl:call-template name="line_th">
	<xsl:with-param name="col" select="$col + 1" />
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="h:table[@class='Detail']/h:tbody/h:tr[1]">
  <FieldDetails>
    <Output>
	<Line bgcolor="iif(r.detailcnt%2,'0xe5e5e5','white')">
	<xsl:call-template name="line_td">
	  <xsl:with-param name="col" select="1" />
	</xsl:call-template>
      </Line>
    </Output>
  </FieldDetails>
</xsl:template>

<xsl:template name="line_td">
  <xsl:param name="col" />
  <xsl:variable name="td_elt"
		select="h:td[position()=$col]" />

  <xsl:choose>
    <xsl:when test="$td_elt">
      <xsl:for-each select="$td_elt">
	<literal width="1"/>
	<xsl:variable name="width"
		      select="string-length(text())"/>
	<field width="{$width}" value="{@title}" align="{@align}" />
	
      </xsl:for-each>
      <xsl:call-template name="line_td">
	<xsl:with-param name="col" select="$col + 1" />
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="h:title | h:link | h:head 
                   | h:body | h:thead | h:tbody | h:tr | h:td">
  <xsl:apply-templates />
</xsl:template>

<xsl:template match="*">
  <xsl:message>no template for: <xsl:value-of select="name()" /></xsl:message>
</xsl:template>

<xsl:template match="text()|@*" mode="Line"/>

<xsl:template match="text()|@*"/>

</xsl:transform>
